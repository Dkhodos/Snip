"""Tests for the redirect router."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from redirect_service.dependencies import get_redirect_manager
from redirect_service.exceptions import LinkExpiredError, LinkNotFoundError
from redirect_service.main import app
from redirect_service.managers.redirect_manager import RedirectResult


def _make_result(**kwargs) -> RedirectResult:
    defaults = dict(
        target_url="https://example.com",
        click_count=1,
        created_by="user1",
        title="My Test Link",
        short_code="abc123",
    )
    defaults.update(kwargs)
    return RedirectResult(**defaults)


class TestRedirectRouter:
    _BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    _SLACK_UA = "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)"
    _TWITTER_UA = "Twitterbot/1.0"

    @pytest.fixture(autouse=True)
    async def _setup(self) -> None:
        app.dependency_overrides.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            self.client = c
            yield
        app.dependency_overrides.clear()

    # --- Browser (non-crawler) behavior ---

    async def test_browser_redirect_returns_302(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = _make_result()
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": self._BROWSER_UA},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://example.com"

    async def test_redirect_passes_user_agent_and_country(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = _make_result()
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": self._BROWSER_UA, "cf-ipcountry": "IL"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        mgr.resolve_redirect.assert_awaited_once_with(
            "abc123", user_agent=self._BROWSER_UA, country="IL"
        )

    # --- Crawler behavior ---

    async def test_crawler_returns_200_html(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = _make_result()
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": self._SLACK_UA},
            follow_redirects=False,
        )
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    async def test_crawler_html_contains_og_title(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = _make_result(title="My Test Link")
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": self._TWITTER_UA},
            follow_redirects=False,
        )
        assert "My Test Link" in resp.text

    async def test_crawler_html_contains_og_image_meta(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = _make_result(short_code="abc123")
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": self._SLACK_UA},
            follow_redirects=False,
        )
        assert 'property="og:image"' in resp.text
        assert "abc123.png" in resp.text

    async def test_crawler_html_contains_refresh_meta(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = _make_result(target_url="https://example.com")
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": self._SLACK_UA},
            follow_redirects=False,
        )
        assert "http-equiv" in resp.text
        assert "https://example.com" in resp.text

    async def test_crawler_html_contains_twitter_card(self) -> None:
        mgr = AsyncMock()
        mgr.resolve_redirect.return_value = _make_result()
        app.dependency_overrides[get_redirect_manager] = lambda: mgr
        resp = await self.client.get(
            "/r/abc123",
            headers={"user-agent": self._TWITTER_UA},
            follow_redirects=False,
        )
        assert "twitter:card" in resp.text
        assert "summary_large_image" in resp.text

    # --- Error cases ---

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
