"""Tests for the health router."""

from tests.unit.base.base_api_test import BaseApiTestCase


class TestHealthRouter(BaseApiTestCase):
    async def test_health(self) -> None:
        resp = await self.client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
