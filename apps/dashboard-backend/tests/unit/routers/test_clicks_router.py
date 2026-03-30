"""Tests for the clicks router."""

from uuid import uuid4

from dashboard_backend.dependencies import get_clicks_manager
from tests.unit.base.base_api_test import BaseApiTestCase


class TestClicksRouter(BaseApiTestCase):
    async def test_aggregate_clicks(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_clicks_manager)
        mgr.get_aggregate_clicks.return_value = {"daily": []}
        resp = await self.client.get("/clicks/aggregate")
        assert resp.status_code == 200

    async def test_link_clicks(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_clicks_manager)
        link_id = uuid4()
        mgr.get_link_clicks.return_value = {
            "link_id": str(link_id),
            "total_clicks": 10,
            "daily": [],
        }
        resp = await self.client.get(f"/links/{link_id}/clicks")
        assert resp.status_code == 200
