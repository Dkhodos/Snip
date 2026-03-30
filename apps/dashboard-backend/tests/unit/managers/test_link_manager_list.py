"""Tests for LinkManager list operations."""

from unittest.mock import AsyncMock

import pytest

from dashboard_backend.exceptions import InvalidSortFieldError
from dashboard_backend.managers.link_manager import LinkManager
from tests.unit.managers.base_link_manager import make_link


class TestLinkManagerList:
    async def test_list_links(self) -> None:
        store = AsyncMock()
        store.list.return_value = ([make_link()], 1)
        manager = LinkManager(store)
        items, total = await manager.list_links("org1")
        assert total == 1

    async def test_invalid_sort(self) -> None:
        store = AsyncMock()
        manager = LinkManager(store)
        with pytest.raises(InvalidSortFieldError):
            await manager.list_links("org1", sort_by="bad_field")
