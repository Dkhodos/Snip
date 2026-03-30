"""Tests for the redirect router."""

from dashboard_backend.dependencies import get_redirect_manager
from tests.unit.base.base_api_test import BaseApiTestCase


class TestRedirectRouter(BaseApiTestCase):
    async def test_redirect(self) -> None:
        mgr = self.override_manager(get_redirect_manager)
        mgr.resolve_redirect.return_value = "https://target.com"
        resp = await self.client.get("/r/abc123", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://target.com"
