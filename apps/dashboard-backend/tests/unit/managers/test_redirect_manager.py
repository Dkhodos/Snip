"""Tests for RedirectManager."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from snip_db.models import Link

from dashboard_backend.exceptions import LinkExpiredError, LinkNotFoundError
from dashboard_backend.managers.redirect_manager import RedirectManager


def _make_link(**overrides) -> Link:
    defaults = {
        "id": uuid4(),
        "org_id": "org1",
        "short_code": "abc",
        "target_url": "https://target.com",
        "is_active": True,
        "click_count": 5,
        "created_by": "user_123",
        "expires_at": None,
    }
    defaults.update(overrides)
    return Link(**defaults)


class TestRedirectManager:
    async def test_resolve_redirect(self) -> None:
        link = _make_link()
        link_store = AsyncMock()
        link_store.get_by_short_code.return_value = link
        link_store.refresh.return_value = None
        click_store = AsyncMock()

        manager = RedirectManager(link_store, click_store)
        result = await manager.resolve_redirect("abc")

        assert result.target_url == "https://target.com"
        assert result.created_by == "user_123"
        link_store.increment_click_count.assert_called_once_with(link)
        click_store.create.assert_called_once()
        link_store.commit.assert_called_once()
        link_store.refresh.assert_called_once_with(link)

    async def test_not_found(self) -> None:
        link_store = AsyncMock()
        link_store.get_by_short_code.return_value = None
        click_store = AsyncMock()

        manager = RedirectManager(link_store, click_store)
        with pytest.raises(LinkNotFoundError):
            await manager.resolve_redirect("missing")

    async def test_expired(self) -> None:
        link = _make_link(expires_at=datetime.utcnow() - timedelta(days=1))
        link_store = AsyncMock()
        link_store.get_by_short_code.return_value = link
        click_store = AsyncMock()

        manager = RedirectManager(link_store, click_store)
        with pytest.raises(LinkExpiredError):
            await manager.resolve_redirect("abc")
