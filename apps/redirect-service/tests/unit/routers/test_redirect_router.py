"""Tests for the redirect router."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from redirect_service.dependencies import get_redirect_manager
from redirect_service.exceptions import LinkExpiredError, LinkNotFoundError
from redirect_service.main import app
from redirect_service.managers.redirect_manager import RedirectResult


class TestRedirectRouter:
    @pytest.fixture(autouse=True)
    async def _setup(self) -> None:
        app.dependency_overrides.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            self.client = c
            yield
        app.dependency_overrides.clear()

    async def test_redirect_returns_302(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = RedirectResult(
            target_url="https://example.com", click_count=1, created_by="user1"
        )
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get("/r/abc123", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://example.com"

    async def test_redirect_passes_user_agent_and_country(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = RedirectResult(
            target_url="https://example.com", click_count=1, created_by="user1"
        )
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": "TestBot/1.0", "cf-ipcountry": "IL"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        mgr.resolve_redirect.assert_awaited_once_with(
            "abc123", user_agent="TestBot/1.0", country="IL"
        )

    async def test_not_found_returns_404(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.side_effect = LinkNotFoundError()
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get("/r/missing")
        assert resp.status_code == 404

    async def test_expired_returns_410(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.side_effect = LinkExpiredError()
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get("/r/expired")
        assert resp.status_code == 410

    async def test_health(self) -> None:
        resp = await self.client.get("/health")
        assert resp.status_code == 200
