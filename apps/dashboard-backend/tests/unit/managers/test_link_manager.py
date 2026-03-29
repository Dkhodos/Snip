"""Tests for LinkManager."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from snip_db.models import Link

from dashboard_backend.exceptions import (
    InvalidSortFieldError,
    LinkNotFoundError,
    ShortCodeCollisionError,
)
from dashboard_backend.managers.link_manager import LinkManager


def _make_link(**overrides) -> Link:
    defaults = {
        "id": uuid4(),
        "org_id": "org1",
        "short_code": "abc123",
        "target_url": "https://example.com",
        "title": "Test",
        "created_by": "user1",
        "click_count": 0,
        "is_active": True,
    }
    defaults.update(overrides)
    return Link(**defaults)


class TestLinkManagerCreate:
    async def test_create_link(self) -> None:
        store = AsyncMock()
        store.get_by_short_code.return_value = None
        store.create.return_value = _make_link()
        manager = LinkManager(store)
        link = await manager.create_link(
            org_id="org1",
            user_id="user1",
            target_url="https://example.com",
            title="Test",
        )
        assert link is not None
        store.create.assert_called_once()
        store.commit.assert_called_once()

    async def test_create_custom_short_code(self) -> None:
        store = AsyncMock()
        store.get_by_short_code.return_value = None
        store.create.return_value = _make_link(short_code="custom")
        manager = LinkManager(store)
        await manager.create_link(
            org_id="org1",
            user_id="user1",
            target_url="https://example.com",
            title="Test",
            custom_short_code="custom",
        )
        store.get_by_short_code.assert_called_once_with("custom")

    async def test_create_collision(self) -> None:
        store = AsyncMock()
        store.get_by_short_code.return_value = _make_link()
        manager = LinkManager(store)
        with pytest.raises(ShortCodeCollisionError):
            await manager.create_link(
                org_id="org1",
                user_id="user1",
                target_url="https://example.com",
                title="Test",
                custom_short_code="taken",
            )


class TestLinkManagerList:
    async def test_list_links(self) -> None:
        store = AsyncMock()
        store.list.return_value = ([_make_link()], 1)
        manager = LinkManager(store)
        items, total = await manager.list_links("org1")
        assert total == 1

    async def test_invalid_sort(self) -> None:
        store = AsyncMock()
        manager = LinkManager(store)
        with pytest.raises(InvalidSortFieldError):
            await manager.list_links("org1", sort_by="bad_field")


class TestLinkManagerGetUpdateDelete:
    async def test_get_link(self) -> None:
        store = AsyncMock()
        expected = _make_link()
        store.get_by_id.return_value = expected
        manager = LinkManager(store)
        assert await manager.get_link(expected.id, "org1") is expected

    async def test_get_link_not_found(self) -> None:
        store = AsyncMock()
        store.get_by_id.return_value = None
        manager = LinkManager(store)
        with pytest.raises(LinkNotFoundError):
            await manager.get_link(uuid4(), "org1")

    async def test_update_link(self) -> None:
        store = AsyncMock()
        link = _make_link()
        store.get_by_id.return_value = link
        store.update.return_value = link
        manager = LinkManager(store)
        await manager.update_link(link.id, "org1", title="New")
        store.update.assert_called_once_with(link, title="New")
        store.commit.assert_called_once()

    async def test_delete_link(self) -> None:
        store = AsyncMock()
        link = _make_link()
        store.get_by_id.return_value = link
        manager = LinkManager(store)
        await manager.delete_link(link.id, "org1")
        store.soft_delete.assert_called_once_with(link)
        store.commit.assert_called_once()

    async def test_get_stats(self) -> None:
        store = AsyncMock()
        stats = {"total_links": 5, "total_clicks": 100, "active_links": 4, "expired_links": 1}
        store.get_stats.return_value = stats
        manager = LinkManager(store)
        assert await manager.get_stats("org1") == stats
