"""Tests for LinkManager get, update, and delete operations."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from dashboard_backend.exceptions import LinkNotFoundError
from dashboard_backend.managers.link_manager import LinkManager
from tests.unit.managers.base_link_manager import make_link


class TestLinkManagerGetUpdateDelete:
    async def test_get_link(self) -> None:
        store = AsyncMock()
        expected = make_link()
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
        link = make_link()
        store.get_by_id.return_value = link
        store.update.return_value = link
        manager = LinkManager(store)
        await manager.update_link(link.id, "org1", title="New")
        store.update.assert_called_once_with(link, title="New")
        store.commit.assert_called_once()

    async def test_delete_link(self) -> None:
        store = AsyncMock()
        link = make_link()
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
