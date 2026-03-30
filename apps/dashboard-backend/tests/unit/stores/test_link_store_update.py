"""Tests for LinkStore update operations."""

from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestLinkStoreUpdate(BaseDBTestCase):
    async def test_update(self) -> None:
        store = LinkStore(self.session)
        link = await store.create(
            org_id="org1",
            short_code="upd1",
            target_url="https://old.com",
            title="Old Title",
            created_by="user1",
        )
        updated = await store.update(link, title="New Title", target_url="https://new.com")
        assert updated.title == "New Title"
        assert updated.target_url == "https://new.com"

    async def test_soft_delete(self) -> None:
        store = LinkStore(self.session)
        link = await store.create(
            org_id="org1",
            short_code="del1",
            target_url="https://example.com",
            title="To Delete",
            created_by="user1",
        )
        assert link.is_active is True
        await store.soft_delete(link)
        assert link.is_active is False

    async def test_increment_click_count(self) -> None:
        store = LinkStore(self.session)
        link = await store.create(
            org_id="org1",
            short_code="clk1",
            target_url="https://example.com",
            title="Clicks",
            created_by="user1",
        )
        assert link.click_count == 0
        await store.increment_click_count(link)
        await self.session.refresh(link)
        assert link.click_count == 1
