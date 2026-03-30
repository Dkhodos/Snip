"""Tests for ClickEventStore query operations."""

from datetime import timedelta

from tests.unit.base.base_test_case import BaseDBTestCase
from tests.unit.stores.base_click_event import seed_clicks


class TestClickEventStoreQueries(BaseDBTestCase):
    async def test_get_daily_clicks_for_link(self) -> None:
        link, store, now = await seed_clicks(self.session)
        since = now - timedelta(days=10)
        daily = await store.get_daily_clicks_for_link(link.id, since)
        assert len(daily) == 5
        total = sum(d["count"] for d in daily)
        assert total == 15  # 1+2+3+4+5

    async def test_get_daily_clicks_for_link_with_recent_filter(self) -> None:
        link, store, now = await seed_clicks(self.session)
        since = now - timedelta(days=2)
        daily = await store.get_daily_clicks_for_link(link.id, since)
        total = sum(d["count"] for d in daily)
        assert total == 6  # day0=1, day1=2, day2=3

    async def test_get_daily_clicks_for_org(self) -> None:
        link, store, now = await seed_clicks(self.session)
        since = now - timedelta(days=10)
        daily = await store.get_daily_clicks_for_org("org1", since)
        total = sum(d["count"] for d in daily)
        assert total == 15

    async def test_get_daily_clicks_for_org_wrong_org(self) -> None:
        _, store, now = await seed_clicks(self.session)
        since = now - timedelta(days=10)
        daily = await store.get_daily_clicks_for_org("other_org", since)
        assert len(daily) == 0
