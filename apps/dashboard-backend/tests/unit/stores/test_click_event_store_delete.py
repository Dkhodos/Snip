"""Tests for ClickEventStore delete operations."""

from datetime import datetime, timedelta

from dashboard_backend.stores.click_event_store import ClickEventStore
from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


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
