"""Tests for LinkStore delete operations."""

from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestLinkStoreDelete(BaseDBTestCase):
    async def test_get_ids_by_org(self) -> None:
        store = LinkStore(self.session)
        await store.create(
            org_id="org1",
            short_code="d1",
            target_url="https://a.com",
            title="A",
            created_by="u",
        )
        await store.create(
            org_id="org1",
            short_code="d2",
            target_url="https://b.com",
            title="B",
            created_by="u",
        )
        ids = await store.get_ids_by_org("org1")
        assert len(ids) == 2

    async def test_delete_by_org(self) -> None:
        store = LinkStore(self.session)
        await store.create(
            org_id="org1",
            short_code="d3",
            target_url="https://a.com",
            title="A",
            created_by="u",
        )
        await store.delete_by_org("org1")
        items, total = await store.list("org1")
        assert total == 0

    async def test_commit(self) -> None:
        store = LinkStore(self.session)
        await store.create(
            org_id="commit_test_org",
            short_code="cm1",
            target_url="https://a.com",
            title="A",
            created_by="u",
        )
        await store.commit()  # should not raise
