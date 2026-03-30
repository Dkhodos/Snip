"""Tests for LinkManager create operations."""

from unittest.mock import AsyncMock

import pytest

from dashboard_backend.exceptions import ShortCodeCollisionError
from dashboard_backend.managers.link_manager import LinkManager
from tests.unit.managers.base_link_manager import make_link


class TestLinkManagerCreate:
    async def test_create_link(self) -> None:
        store = AsyncMock()
        store.get_by_short_code.return_value = None
        store.create.return_value = make_link()
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
        store.create.return_value = make_link(short_code="custom")
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
        store.get_by_short_code.return_value = make_link()
        manager = LinkManager(store)
        with pytest.raises(ShortCodeCollisionError):
            await manager.create_link(
                org_id="org1",
                user_id="user1",
                target_url="https://example.com",
                title="Test",
                custom_short_code="taken",
            )
