"""Tests for LinkStore list operations."""

from datetime import datetime, timedelta

from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


async def _seed(store: LinkStore, count: int = 5) -> None:
    """Seed the store with test links."""
    now = datetime.utcnow()
    for i in range(count):
        await store.create(
            org_id="org1",
            short_code=f"code{i}",
            target_url=f"https://example.com/{i}",
            title=f"Link {i}",
            created_by="user1",
            click_count=i * 10,
            is_active=i % 2 == 0,
            created_at=now - timedelta(days=count - i),
        )


class TestLinkStoreList(BaseDBTestCase):
    async def test_list_basic(self) -> None:
        store = LinkStore(self.session)
        await _seed(store)
        items, total = await store.list("org1")
        assert total == 5
        assert len(items) == 5

    async def test_list_pagination(self) -> None:
        store = LinkStore(self.session)
        await _seed(store, 10)
        items, total = await store.list("org1", page=2, limit=3)
        assert total == 10
        assert len(items) == 3

    async def test_list_search(self) -> None:
        store = LinkStore(self.session)
        await _seed(store)
        items, total = await store.list("org1", search="Link 3")
        assert total == 1
        assert items[0].title == "Link 3"

    async def test_list_status_active(self) -> None:
        store = LinkStore(self.session)
        await _seed(store)
        items, total = await store.list("org1", status="active")
        assert all(item.is_active for item in items)

    async def test_list_status_inactive(self) -> None:
        store = LinkStore(self.session)
        await _seed(store)
        items, total = await store.list("org1", status="inactive")
        assert all(not item.is_active for item in items)

    async def test_list_status_expired(self) -> None:
        store = LinkStore(self.session)
        await store.create(
            org_id="org1",
            short_code="expired1",
            target_url="https://example.com",
            title="Expired",
            created_by="user1",
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        items, total = await store.list("org1", status="expired")
        assert total == 1

    async def test_list_sort_asc(self) -> None:
        store = LinkStore(self.session)
        await _seed(store)
        items, _ = await store.list("org1", sort_by="click_count", sort_order="asc")
        counts = [item.click_count for item in items]
        assert counts == sorted(counts)

    async def test_list_wrong_org(self) -> None:
        store = LinkStore(self.session)
        await _seed(store)
        items, total = await store.list("other_org")
        assert total == 0
