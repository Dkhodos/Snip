"""Tests for the seed router."""

from unittest.mock import patch

from dashboard_backend.dependencies import get_seed_manager
from tests.unit.base.base_api_test import BaseApiTestCase


class TestSeedRouter(BaseApiTestCase):
    async def test_seed(self) -> None:
        mgr = self.override_manager(get_seed_manager)
        mgr.seed.return_value = {"message": "ok", "links_created": 25}
        resp = await self.client.post("/dev/seed")
        assert resp.status_code == 200

    async def test_seed_blocked_in_production(self) -> None:
        self.override_manager(get_seed_manager)
        with patch("dashboard_backend.routers.seed.settings") as mock_settings:
            mock_settings.environment = "production"
            resp = await self.client.post("/dev/seed")
            assert resp.status_code == 403
