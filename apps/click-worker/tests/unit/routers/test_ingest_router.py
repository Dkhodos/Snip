"""Tests for the ingest router."""

import base64
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from click_worker.dependencies import get_analytics_client, verify_pubsub_token
from click_worker.main import app

_PATCH_VERIFY_TOKEN = "click_worker.dependencies.google.oauth2.id_token.verify_oauth2_token"


def _make_envelope(data: dict) -> dict:
    """Create a Pub/Sub push envelope from a click event dict."""
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    return {
        "message": {"data": encoded, "message_id": "msg_123"},
        "subscription": "projects/test/subscriptions/test-sub",
    }


def _valid_click_data() -> dict:
    return {
        "event_id": "evt_001",
        "link_id": "link_001",
        "short_code": "abc",
        "org_id": "org_001",
        "clicked_at": datetime.now(tz=UTC).isoformat(),
        "user_agent": "Mozilla/5.0",
        "country": None,
    }


def _bypass_auth(app_) -> None:
    """Override auth so tests focus on business logic, not token verification."""
    app_.dependency_overrides[verify_pubsub_token] = lambda: None


class TestIngestRouterAuthDisabled:
    """Existing behaviour with auth bypassed (enable_pubsub_auth=False path)."""

    @pytest.fixture(autouse=True)
    async def _setup(self) -> None:
        app.dependency_overrides.clear()
        _bypass_auth(app)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            self.client = c
            yield
        app.dependency_overrides.clear()

    async def test_ingest_valid_message(self) -> None:
        analytics = AsyncMock()
        app.dependency_overrides[get_analytics_client] = lambda: analytics
        envelope = _make_envelope(_valid_click_data())
        resp = await self.client.post("/ingest", json=envelope)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        analytics.insert_click_event.assert_called_once()

    async def test_ingest_malformed_message_acks(self) -> None:
        analytics = AsyncMock()
        app.dependency_overrides[get_analytics_client] = lambda: analytics
        encoded = base64.b64encode(b"not json").decode()
        envelope = {"message": {"data": encoded}, "subscription": ""}
        resp = await self.client.post("/ingest", json=envelope)
        assert resp.status_code == 200
        assert resp.json()["status"] == "acked_malformed"
        analytics.insert_click_event.assert_not_called()

    async def test_ingest_analytics_failure_returns_500(self) -> None:
        analytics = AsyncMock()
        analytics.insert_click_event.side_effect = RuntimeError("BQ down")
        app.dependency_overrides[get_analytics_client] = lambda: analytics
        envelope = _make_envelope(_valid_click_data())
        resp = await self.client.post("/ingest", json=envelope)
        assert resp.status_code == 500

    async def test_health(self) -> None:
        resp = await self.client.get("/health")
        assert resp.status_code == 200


class TestIngestRouterAuthEnabled:
    """CRIT-3: /ingest must reject requests without a valid Pub/Sub OIDC token."""

    _AUDIENCE = "https://click-worker.example.com/ingest"

    @pytest.fixture(autouse=True)
    async def _setup(self) -> None:
        app.dependency_overrides.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            self.client = c
            yield
        app.dependency_overrides.clear()

    async def test_no_authorization_header_returns_401(self) -> None:
        app.dependency_overrides[get_analytics_client] = lambda: AsyncMock()
        with (
            patch("click_worker.dependencies.settings.enable_pubsub_auth", True),
            patch("click_worker.dependencies.settings.pubsub_audience", self._AUDIENCE),
        ):
            envelope = _make_envelope(_valid_click_data())
            resp = await self.client.post("/ingest", json=envelope)
        assert resp.status_code == 401

    async def test_invalid_bearer_token_returns_401(self) -> None:
        app.dependency_overrides[get_analytics_client] = lambda: AsyncMock()
        with (
            patch("click_worker.dependencies.settings.enable_pubsub_auth", True),
            patch("click_worker.dependencies.settings.pubsub_audience", self._AUDIENCE),
            patch(_PATCH_VERIFY_TOKEN) as mock_verify,
        ):
            mock_verify.side_effect = ValueError("Token invalid")
            envelope = _make_envelope(_valid_click_data())
            resp = await self.client.post(
                "/ingest",
                json=envelope,
                headers={"Authorization": "Bearer bad.token.here"},
            )
        assert resp.status_code == 401

    async def test_missing_bearer_prefix_returns_401(self) -> None:
        app.dependency_overrides[get_analytics_client] = lambda: AsyncMock()
        with (
            patch("click_worker.dependencies.settings.enable_pubsub_auth", True),
            patch("click_worker.dependencies.settings.pubsub_audience", self._AUDIENCE),
        ):
            envelope = _make_envelope(_valid_click_data())
            resp = await self.client.post(
                "/ingest",
                json=envelope,
                headers={"Authorization": "Token not-bearer"},
            )
        assert resp.status_code == 401

    async def test_valid_token_proceeds_to_ingest(self) -> None:
        analytics = AsyncMock()
        app.dependency_overrides[get_analytics_client] = lambda: analytics
        with (
            patch("click_worker.dependencies.settings.enable_pubsub_auth", True),
            patch("click_worker.dependencies.settings.pubsub_audience", self._AUDIENCE),
            patch(_PATCH_VERIFY_TOKEN) as mock_verify,
        ):
            mock_verify.return_value = {"email": "pubsub@gcp.iam.gserviceaccount.com"}
            envelope = _make_envelope(_valid_click_data())
            resp = await self.client.post(
                "/ingest",
                json=envelope,
                headers={"Authorization": "Bearer valid.jwt.token"},
            )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_auth_disabled_bypasses_token_check(self) -> None:
        analytics = AsyncMock()
        app.dependency_overrides[get_analytics_client] = lambda: analytics
        with patch("click_worker.dependencies.settings.enable_pubsub_auth", False):
            envelope = _make_envelope(_valid_click_data())
            # No Authorization header — should pass because auth is disabled
            resp = await self.client.post("/ingest", json=envelope)
        assert resp.status_code == 200
