"""Redirect business logic manager."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from snip_db.stores.link_store import LinkStore
from snip_logger import get_logger
from snip_queue import ClickEventMessage, QueuePublisher
from snip_telemetry import traced

from redirect_service.exceptions import LinkExpiredError, LinkNotFoundError

_log = get_logger("redirect-service", log_prefix="RedirectManager")


@dataclass(frozen=True)
class RedirectResult:
    target_url: str
    click_count: int
    created_by: Optional[str]
    title: Optional[str] = None
    short_code: str = ""


class RedirectManager:
    def __init__(
        self,
        link_store: LinkStore,
        publisher: QueuePublisher,
        click_topic: str,
    ) -> None:
        self._link_store = link_store
        self._publisher = publisher
        self._click_topic = click_topic

    @traced
    async def resolve_redirect(
        self,
        short_code: str,
        *,
        user_agent: str | None = None,
        country: str | None = None,
    ) -> RedirectResult:
        link = await self._link_store.get_by_short_code(short_code, active_only=True)
        if not link:
            raise LinkNotFoundError()

        now = datetime.utcnow()
        if link.expires_at and link.expires_at < now:
            raise LinkExpiredError()

        # Increment click count in Postgres (synchronous, transactional)
        await self._link_store.increment_click_count(link)
        await self._link_store.commit()
        await self._link_store.refresh(link)

        # Publish click event to queue (fire-and-forget)
        try:
            message = ClickEventMessage(
                link_id=str(link.id),
                short_code=short_code,
                org_id=link.org_id,
                clicked_at=now,
                user_agent=user_agent,
                country=country,
            )
            await self._publisher.publish(self._click_topic, message.to_json())
        except Exception:
            _log.warning(
                "click_event_publish_failed",
                short_code=short_code,
                exc_info=True,
            )

        result = RedirectResult(
            target_url=link.target_url,
            click_count=link.click_count,
            created_by=link.created_by,
            title=link.title,
            short_code=short_code,
        )
        _log.info("redirect_resolved", short_code=short_code, click_count=result.click_count)
        return result
