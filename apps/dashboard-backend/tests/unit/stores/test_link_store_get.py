"""Tests for LinkStore get operations."""

from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase
from tests.unit.stores.base_link_store import create_link


class TestLinkStoreGet(BaseDBTestCase):
    async def test_get_by_id(self) -> None:
        store = LinkStore(self.session)
        link = await create_link(store)
        found = await store.get_by_id(link.id, "org1")
        assert found is not None
        assert found.id == link.id

    async def test_get_by_id_wrong_org(self) -> None:
        store = LinkStore(self.session)
        link = await create_link(store)
        found = await store.get_by_id(link.id, "other_org")
        assert found is None

    async def test_get_by_short_code(self) -> None:
        store = LinkStore(self.session)
        await create_link(store, short_code="findme")
        found = await store.get_by_short_code("findme")
        assert found is not None
        assert found.short_code == "findme"

    async def test_get_by_short_code_active_only(self) -> None:
        store = LinkStore(self.session)
        await create_link(store, short_code="inactive1", is_active=False)
        found = await store.get_by_short_code("inactive1", active_only=True)
        assert found is None

    async def test_get_by_short_code_not_found(self) -> None:
        store = LinkStore(self.session)
        found = await store.get_by_short_code("nonexistent")
        assert found is None
