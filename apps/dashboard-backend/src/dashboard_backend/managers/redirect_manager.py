"""Redirect business logic manager."""

from datetime import datetime

from snip_db.stores.click_event_store import ClickEventStore
from snip_db.stores.link_store import LinkStore

from dashboard_backend.exceptions import LinkExpiredError, LinkNotFoundError


class RedirectManager:
    def __init__(self, link_store: LinkStore, click_event_store: ClickEventStore) -> None:
        self._link_store = link_store
        self._click_event_store = click_event_store

    async def resolve_redirect(self, short_code: str) -> str:
        link = await self._link_store.get_by_short_code(short_code, active_only=True)
        if not link:
            raise LinkNotFoundError()

        if link.expires_at and link.expires_at < datetime.utcnow():
            raise LinkExpiredError()

        await self._link_store.increment_click_count(link)
        await self._click_event_store.create(link_id=link.id, clicked_at=datetime.utcnow())
        await self._link_store.commit()

        return link.target_url
