"""Tests for the flags router."""

from dashboard_backend.dependencies import get_feature_flag_manager
from tests.unit.base.base_api_test import BaseApiTestCase


class TestFlagsRouter(BaseApiTestCase):
    async def test_get_flags(self) -> None:
        mgr = self.override_manager(get_feature_flag_manager)
        mgr.get_all_flags.return_value = {"flag_a": True}
        resp = await self.client.get("/flags")
        assert resp.status_code == 200
        assert resp.json() == {"flag_a": True}
