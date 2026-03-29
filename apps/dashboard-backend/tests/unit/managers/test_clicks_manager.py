"""Tests for ClicksManager."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from snip_db.models import Link

from dashboard_backend.exceptions import LinkNotFoundError
from dashboard_backend.managers.clicks_manager import ClicksManager


def _make_link(**overrides) -> Link:
    defaults = {
        "id": uuid4(),
        "org_id": "org1",
        "short_code": "x",
        "target_url": "https://x.com",
        "click_count": 42,
    }
    defaults.update(overrides)
    return Link(**defaults)


class TestClicksManager:
    async def test_get_link_clicks(self) -> None:
        link = _make_link()
        link_store = AsyncMock()
        link_store.get_by_id.return_value = link
        click_store = AsyncMock()
        click_store.get_daily_clicks_for_link.return_value = [{"date": "2026-03-29", "count": 5}]

        manager = ClicksManager(link_store, click_store)
        result = await manager.get_link_clicks(link.id, "org1")

        assert result["link_id"] == str(link.id)
        assert result["total_clicks"] == 42
        assert len(result["daily"]) == 1

    async def test_get_link_clicks_not_found(self) -> None:
        link_store = AsyncMock()
        link_store.get_by_id.return_value = None
        click_store = AsyncMock()

        manager = ClicksManager(link_store, click_store)
        with pytest.raises(LinkNotFoundError):
            await manager.get_link_clicks(uuid4(), "org1")

    async def test_get_aggregate_clicks(self) -> None:
        link_store = AsyncMock()
        click_store = AsyncMock()
        click_store.get_daily_clicks_for_org.return_value = [
            {"date": "2026-03-28", "count": 10},
            {"date": "2026-03-29", "count": 20},
        ]

        manager = ClicksManager(link_store, click_store)
        result = await manager.get_aggregate_clicks("org1")

        assert len(result["daily"]) == 2
