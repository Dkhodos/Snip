"""Click event data access store."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select

from snip_db.models import ClickEvent, Link
from snip_db.stores.base_store import BaseStore

_log = logging.getLogger(__name__)


class ClickEventStore(BaseStore[ClickEvent]):
    model = ClickEvent

    async def create(
        self,
        *,
        link_id: UUID,
        clicked_at: datetime,
        user_agent: str | None = None,
        country: str | None = None,
        event_id: UUID | None = None,
    ) -> ClickEvent:
        kwargs: dict = {
            "link_id": link_id,
            "clicked_at": clicked_at,
            "user_agent": user_agent,
            "country": country,
        }
        if event_id is not None:
            kwargs["id"] = event_id

        event = ClickEvent(**kwargs)
        self._add(event)
        await self.flush()
        _log.debug(f"click_event_created link_id={link_id}")
        return event

    async def get_daily_clicks_for_link(self, link_id: UUID, since: datetime) -> list[dict]:
        query = (
            select(
                func.date(ClickEvent.clicked_at).label("date"),
                func.count().label("count"),
            )
            .where(ClickEvent.link_id == link_id, ClickEvent.clicked_at >= since)
            .group_by(func.date(ClickEvent.clicked_at))
            .order_by(func.date(ClickEvent.clicked_at))
        )
        result = await self._session.execute(query)
        return [{"date": str(row.date), "count": row.count} for row in result]

    async def get_daily_clicks_for_org(self, org_id: str, since: datetime) -> list[dict]:
        query = (
            select(
                func.date(ClickEvent.clicked_at).label("date"),
                func.count().label("count"),
            )
            .join(Link, ClickEvent.link_id == Link.id)
            .where(Link.org_id == org_id, ClickEvent.clicked_at >= since)
            .group_by(func.date(ClickEvent.clicked_at))
            .order_by(func.date(ClickEvent.clicked_at))
        )
        result = await self._session.execute(query)
        return [{"date": str(row.date), "count": row.count} for row in result]

    async def delete_by_link_ids(self, link_ids: list[UUID]) -> None:
        if link_ids:
            await self._session.execute(delete(ClickEvent).where(ClickEvent.link_id.in_(link_ids)))
            _log.info(f"click_events_deleted count={len(link_ids)}")
