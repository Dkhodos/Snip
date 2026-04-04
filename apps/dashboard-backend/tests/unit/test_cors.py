"""Tests for CORS configuration — HIGH-5."""

import pytest
from httpx import ASGITransport, AsyncClient

from dashboard_backend.main import app

_ALLOWED_ORIGIN = "http://localhost:5173"
_DISALLOWED_ORIGIN = "https://evil.example.com"


class TestCors:
    @pytest.fixture(autouse=True)
    async def _setup(self) -> None:
        app.dependency_overrides.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            self.client = c
            yield
        app.dependency_overrides.clear()

    async def test_preflight_allowed_origin_returns_cors_headers(self) -> None:
        resp = await self.client.options(
            "/links",
            headers={
                "Origin": _ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == _ALLOWED_ORIGIN

    async def test_preflight_disallowed_origin_returns_no_cors_header(self) -> None:
        resp = await self.client.options(
            "/links",
            headers={
                "Origin": _DISALLOWED_ORIGIN,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in resp.headers

    async def test_allowed_methods_present_in_preflight(self) -> None:
        resp = await self.client.options(
            "/links",
            headers={
                "Origin": _ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        allowed = resp.headers.get("access-control-allow-methods", "")
        for method in ("GET", "POST", "PATCH", "DELETE"):
            assert method in allowed, f"{method} missing from allowed methods"

    async def test_put_method_not_in_allowed_methods(self) -> None:
        resp = await self.client.options(
            "/links",
            headers={
                "Origin": _ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "PUT",
            },
        )
        # PUT should not be listed as an allowed method
        allowed = resp.headers.get("access-control-allow-methods", "")
        assert "PUT" not in allowed

    async def test_allowed_headers_present_in_preflight(self) -> None:
        resp = await self.client.options(
            "/links",
            headers={
                "Origin": _ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )
        allowed = resp.headers.get("access-control-allow-headers", "")
        assert "authorization" in allowed.lower()
        assert "content-type" in allowed.lower()
