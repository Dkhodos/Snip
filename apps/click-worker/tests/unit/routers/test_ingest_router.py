"""Tests for the ingest router."""

import base64
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from click_worker.dependencies import get_analytics_client
from click_worker.main import app


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


class TestIngestRouter:
    @pytest.fixture(autouse=True)
    async def _setup(self) -> None:
        app.dependency_overrides.clear()
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
