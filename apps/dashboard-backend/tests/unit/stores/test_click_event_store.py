"""Tests for ClickEventStore."""

from datetime import datetime, timedelta
from uuid import uuid4

from dashboard_backend.stores.click_event_store import ClickEventStore
from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestClickEventStoreCreate(BaseDBTestCase):
    async def _make_link(self) -> object:
        store = LinkStore(self.session)
        return await store.create(
            org_id="org1",
            short_code=f"lnk{uuid4().hex[:6]}",
            target_url="https://example.com",
            title="Test",
            created_by="user1",
        )

    async def test_create_event(self) -> None:
        link = await self._make_link()
        store = ClickEventStore(self.session)
        now = datetime.utcnow()
        event = await store.create(link_id=link.id, clicked_at=now)
        assert event.link_id == link.id
        assert event.clicked_at == now
        assert event.user_agent is None

    async def test_create_event_with_metadata(self) -> None:
        link = await self._make_link()
        store = ClickEventStore(self.session)
        event_id = uuid4()
        event = await store.create(
            event_id=event_id,
            link_id=link.id,
            clicked_at=datetime.utcnow(),
            user_agent="Mozilla/5.0",
            country="US",
        )
        assert event.id == event_id
        assert event.user_agent == "Mozilla/5.0"
        assert event.country == "US"


class TestClickEventStoreQueries(BaseDBTestCase):
    async def _seed_clicks(self) -> tuple:
        link_store = LinkStore(self.session)
        click_store = ClickEventStore(self.session)
        now = datetime.utcnow()

        link = await link_store.create(
            org_id="org1",
            short_code="qlink1",
            target_url="https://example.com",
            title="Query Link",
            created_by="user1",
        )

        # Create clicks over several days
        for day in range(5):
            for _ in range(day + 1):  # 1, 2, 3, 4, 5 clicks per day
                await click_store.create(
                    link_id=link.id,
                    clicked_at=now - timedelta(days=day),
                )

        return link, click_store, now

    async def test_get_daily_clicks_for_link(self) -> None:
        link, store, now = await self._seed_clicks()
        since = now - timedelta(days=10)
        daily = await store.get_daily_clicks_for_link(link.id, since)
        assert len(daily) == 5
        total = sum(d["count"] for d in daily)
        assert total == 15  # 1+2+3+4+5

    async def test_get_daily_clicks_for_link_with_recent_filter(self) -> None:
        link, store, now = await self._seed_clicks()
        since = now - timedelta(days=2)
        daily = await store.get_daily_clicks_for_link(link.id, since)
        total = sum(d["count"] for d in daily)
        assert total == 6  # day0=1, day1=2, day2=3

    async def test_get_daily_clicks_for_org(self) -> None:
        link, store, now = await self._seed_clicks()
        since = now - timedelta(days=10)
        daily = await store.get_daily_clicks_for_org("org1", since)
        total = sum(d["count"] for d in daily)
        assert total == 15

    async def test_get_daily_clicks_for_org_wrong_org(self) -> None:
        _, store, now = await self._seed_clicks()
        since = now - timedelta(days=10)
        daily = await store.get_daily_clicks_for_org("other_org", since)
        assert len(daily) == 0


class TestClickEventStoreDelete(BaseDBTestCase):
    async def test_delete_by_link_ids(self) -> None:
        link_store = LinkStore(self.session)
        click_store = ClickEventStore(self.session)

        link = await link_store.create(
            org_id="org1",
            short_code="delclk",
            target_url="https://example.com",
            title="Test",
            created_by="user1",
        )
        await click_store.create(link_id=link.id, clicked_at=datetime.utcnow())
        await click_store.create(link_id=link.id, clicked_at=datetime.utcnow())

        await click_store.delete_by_link_ids([link.id])
        daily = await click_store.get_daily_clicks_for_link(
            link.id, datetime.utcnow() - timedelta(days=1)
        )
        assert len(daily) == 0

    async def test_delete_by_empty_link_ids(self) -> None:
        store = ClickEventStore(self.session)
        await store.delete_by_link_ids([])  # should not raise

    async def test_commit(self) -> None:
        store = ClickEventStore(self.session)
        await store.commit()  # should not raise
