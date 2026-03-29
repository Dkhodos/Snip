"""Tests for SeedManager."""

from dashboard_backend.managers.seed_manager import SeedManager
from dashboard_backend.stores.click_event_store import ClickEventStore
from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestSeedManager(BaseDBTestCase):
    async def test_seed_creates_25_links(self) -> None:
        link_store = LinkStore(self.session)
        click_store = ClickEventStore(self.session)
        manager = SeedManager(link_store, click_store)

        result = await manager.seed("test_org")

        assert result["links_created"] == 25
        items, total = await link_store.list("test_org", limit=100)
        assert total == 25

    async def test_seed_is_idempotent(self) -> None:
        link_store = LinkStore(self.session)
        click_store = ClickEventStore(self.session)
        manager = SeedManager(link_store, click_store)

        await manager.seed("test_org")
        await manager.seed("test_org")

        _, total = await link_store.list("test_org", limit=100)
        assert total == 25
