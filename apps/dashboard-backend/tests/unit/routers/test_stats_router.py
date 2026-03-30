"""Tests for the stats router."""

from dashboard_backend.dependencies import get_link_manager
from tests.unit.base.base_api_test import BaseApiTestCase


class TestStatsRouter(BaseApiTestCase):
    async def test_get_stats(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.get_stats.return_value = {
            "total_links": 5,
            "total_clicks": 100,
            "active_links": 4,
            "expired_links": 1,
        }
        resp = await self.client.get("/stats")
        assert resp.status_code == 200
