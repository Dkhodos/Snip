"""Clicks analytics business logic manager."""

from datetime import datetime, timedelta
from uuid import UUID

from snip_db.stores.click_event_store import ClickEventStore
from snip_db.stores.link_store import LinkStore
from snip_logger import get_logger

from dashboard_backend.exceptions import LinkNotFoundError

_log = get_logger("dashboard-backend", log_prefix="ClicksManager")


class ClicksManager:
    def __init__(self, link_store: LinkStore, click_event_store: ClickEventStore) -> None:
        self._link_store = link_store
        self._click_event_store = click_event_store

    async def get_link_clicks(self, link_id: UUID, org_id: str) -> dict:
        link = await self._link_store.get_by_id(link_id, org_id)
        if not link:
            raise LinkNotFoundError()

        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily = await self._click_event_store.get_daily_clicks_for_link(link_id, seven_days_ago)

        result = {
            "link_id": str(link_id),
            "total_clicks": link.click_count,
            "daily": daily,
        }
        _log.info("link_clicks_fetched", link_id=str(link_id), total_clicks=link.click_count)
        return result

    async def get_aggregate_clicks(self, org_id: str) -> dict:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily = await self._click_event_store.get_daily_clicks_for_org(org_id, thirty_days_ago)
        _log.info("aggregate_clicks_fetched", org_id=org_id, days=len(daily))
        return {"daily": daily}
