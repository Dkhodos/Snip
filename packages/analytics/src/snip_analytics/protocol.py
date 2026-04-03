"""Analytics client protocol."""

from typing import Protocol

from snip_analytics.models import ClickEventRow, DailyClickCount


class AnalyticsClient(Protocol):
    """Protocol for analytics read/write operations."""

    async def insert_click_event(self, event: ClickEventRow) -> None:
        """Insert a click event into the analytics store."""
        ...

    async def get_daily_clicks_for_link(
        self, link_id: str, *, days: int = 7
    ) -> list[DailyClickCount]:
        """Get daily click counts for a specific link."""
        ...

    async def get_daily_clicks_for_org(
        self, org_id: str, *, days: int = 30
    ) -> list[DailyClickCount]:
        """Get daily click counts for an entire organization."""
        ...
