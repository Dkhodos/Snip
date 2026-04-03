"""Dev analytics client with in-memory storage for local development."""

import logging
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from snip_analytics.models import ClickEventRow, DailyClickCount
from snip_analytics.protocol import AnalyticsClient

_log = logging.getLogger(__name__)


class DevAnalyticsClient:
    """In-memory analytics client for local development.

    Stores click events in memory and supports the same query interface
    as the BigQuery client. Data is lost on restart.
    """

    def __init__(self) -> None:
        self._events: list[ClickEventRow] = []

    async def insert_click_event(self, event: ClickEventRow) -> None:
        self._events.append(event)
        _log.info(
            "click_event_inserted provider=dev event_id=%s link_id=%s",
            event.event_id,
            event.link_id,
        )

    async def get_daily_clicks_for_link(
        self, link_id: str, *, days: int = 7
    ) -> list[DailyClickCount]:
        since = datetime.now(tz=UTC) - timedelta(days=days)
        counts: dict[str, int] = defaultdict(int)
        for event in self._events:
            if event.link_id == link_id and event.clicked_at >= since:
                date_str = event.clicked_at.strftime("%Y-%m-%d")
                counts[date_str] += 1
        return [DailyClickCount(date=d, count=c) for d, c in sorted(counts.items())]

    async def get_daily_clicks_for_org(
        self, org_id: str, *, days: int = 30
    ) -> list[DailyClickCount]:
        since = datetime.now(tz=UTC) - timedelta(days=days)
        counts: dict[str, int] = defaultdict(int)
        for event in self._events:
            if event.org_id == org_id and event.clicked_at >= since:
                date_str = event.clicked_at.strftime("%Y-%m-%d")
                counts[date_str] += 1
        return [DailyClickCount(date=d, count=c) for d, c in sorted(counts.items())]


def _assert_implements_protocol() -> None:
    _: AnalyticsClient = DevAnalyticsClient()  # noqa: F841
