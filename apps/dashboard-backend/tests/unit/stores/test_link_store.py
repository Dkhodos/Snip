"""Tests for LinkStore."""

from datetime import datetime, timedelta

from dashboard_backend.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestLinkStoreCreate(BaseDBTestCase):
    async def test_create_link(self) -> None:
        store = LinkStore(self.session)
        link = await store.create(
            org_id="org1",
            short_code="abc123",
            target_url="https://example.com",
            title="Test Link",
            created_by="user1",
        )
        assert link.id is not None
        assert link.org_id == "org1"
        assert link.short_code == "abc123"
        assert link.target_url == "https://example.com"
        assert link.title == "Test Link"
        assert link.click_count == 0
        assert link.is_active is True

    async def test_create_with_optional_fields(self) -> None:
        store = LinkStore(self.session)
        from uuid import uuid4

        link_id = uuid4()
        now = datetime.utcnow()
        expires = now + timedelta(days=30)

        link = await store.create(
            link_id=link_id,
            org_id="org1",
            short_code="xyz789",
            target_url="https://example.com",
            title="Full Link",
            created_by="user1",
            click_count=42,
            is_active=False,
            created_at=now,
            expires_at=expires,
        )
        assert link.id == link_id
        assert link.click_count == 42
        assert link.is_active is False
        assert link.expires_at == expires


class TestLinkStoreGet(BaseDBTestCase):
    async def _create_link(self, store: LinkStore, **overrides) -> object:
        defaults = {
            "org_id": "org1",
            "short_code": "abc123",
            "target_url": "https://example.com",
            "title": "Test",
            "created_by": "user1",
        }
        defaults.update(overrides)
        return await store.create(**defaults)

    async def test_get_by_id(self) -> None:
        store = LinkStore(self.session)
        link = await self._create_link(store)
        found = await store.get_by_id(link.id, "org1")
        assert found is not None
        assert found.id == link.id

    async def test_get_by_id_wrong_org(self) -> None:
        store = LinkStore(self.session)
        link = await self._create_link(store)
        found = await store.get_by_id(link.id, "other_org")
        assert found is None

    async def test_get_by_short_code(self) -> None:
        store = LinkStore(self.session)
        await self._create_link(store, short_code="findme")
        found = await store.get_by_short_code("findme")
        assert found is not None
        assert found.short_code == "findme"

    async def test_get_by_short_code_active_only(self) -> None:
        store = LinkStore(self.session)
        await self._create_link(store, short_code="inactive1", is_active=False)
        found = await store.get_by_short_code("inactive1", active_only=True)
        assert found is None

    async def test_get_by_short_code_not_found(self) -> None:
        store = LinkStore(self.session)
        found = await store.get_by_short_code("nonexistent")
        assert found is None


class TestLinkStoreList(BaseDBTestCase):
    async def _seed(self, store: LinkStore, count: int = 5) -> None:
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

    async def test_list_basic(self) -> None:
        store = LinkStore(self.session)
        await self._seed(store)
        items, total = await store.list("org1")
        assert total == 5
        assert len(items) == 5

    async def test_list_pagination(self) -> None:
        store = LinkStore(self.session)
        await self._seed(store, 10)
        items, total = await store.list("org1", page=2, limit=3)
        assert total == 10
        assert len(items) == 3

    async def test_list_search(self) -> None:
        store = LinkStore(self.session)
        await self._seed(store)
        items, total = await store.list("org1", search="Link 3")
        assert total == 1
        assert items[0].title == "Link 3"

    async def test_list_status_active(self) -> None:
        store = LinkStore(self.session)
        await self._seed(store)
        items, total = await store.list("org1", status="active")
        assert all(item.is_active for item in items)

    async def test_list_status_inactive(self) -> None:
        store = LinkStore(self.session)
        await self._seed(store)
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
        await self._seed(store)
        items, _ = await store.list("org1", sort_by="click_count", sort_order="asc")
        counts = [item.click_count for item in items]
        assert counts == sorted(counts)

    async def test_list_wrong_org(self) -> None:
        store = LinkStore(self.session)
        await self._seed(store)
        items, total = await store.list("other_org")
        assert total == 0


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


class TestLinkStoreStats(BaseDBTestCase):
    async def test_get_stats(self) -> None:
        store = LinkStore(self.session)
        # Active link
        await store.create(
            org_id="org1",
            short_code="s1",
            target_url="https://a.com",
            title="A",
            created_by="u",
            click_count=10,
        )
        # Inactive link
        await store.create(
            org_id="org1",
            short_code="s2",
            target_url="https://b.com",
            title="B",
            created_by="u",
            is_active=False,
            click_count=5,
        )
        # Expired link
        await store.create(
            org_id="org1",
            short_code="s3",
            target_url="https://c.com",
            title="C",
            created_by="u",
            click_count=3,
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        stats = await store.get_stats("org1")
        assert stats["total_links"] == 3
        assert stats["total_clicks"] == 18
        assert stats["active_links"] == 2  # s1 + s3 (expired but still is_active=True)
        assert stats["expired_links"] == 1


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
            org_id="org1",
            short_code="cm1",
            target_url="https://a.com",
            title="A",
            created_by="u",
        )
        await store.commit()  # should not raise
