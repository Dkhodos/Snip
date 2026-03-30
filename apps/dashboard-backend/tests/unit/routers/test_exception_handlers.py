"""Tests for exception handlers."""

from dashboard_backend.dependencies import (
    get_current_user,
    get_link_manager,
    get_redirect_manager,
)
from dashboard_backend.exceptions import (
    AuthenticationError,
    InvalidSortFieldError,
    LinkExpiredError,
    LinkNotFoundError,
    OrganizationRequiredError,
    ShortCodeCollisionError,
)
from dashboard_backend.main import app
from tests.unit.base.base_api_test import BaseApiTestCase


class TestExceptionHandlers(BaseApiTestCase):
    async def test_link_not_found(self) -> None:
        mgr = self.override_manager(get_redirect_manager)
        mgr.resolve_redirect.side_effect = LinkNotFoundError()
        resp = await self.client.get("/r/missing", follow_redirects=False)
        assert resp.status_code == 404

    async def test_link_expired(self) -> None:
        mgr = self.override_manager(get_redirect_manager)
        mgr.resolve_redirect.side_effect = LinkExpiredError()
        resp = await self.client.get("/r/expired", follow_redirects=False)
        assert resp.status_code == 410

    async def test_short_code_collision(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.create_link.side_effect = ShortCodeCollisionError()
        resp = await self.client.post(
            "/links",
            json={
                "target_url": "https://example.com",
                "title": "Test",
            },
        )
        assert resp.status_code == 409

    async def test_invalid_sort_field(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.list_links.side_effect = InvalidSortFieldError({"a", "b"})
        resp = await self.client.get("/links")
        assert resp.status_code == 400

    async def test_auth_error(self) -> None:
        async def fail_auth():
            raise AuthenticationError("bad token")

        app.dependency_overrides[get_current_user] = fail_auth
        resp = await self.client.get("/links")
        assert resp.status_code == 401

    async def test_org_required_error(self) -> None:
        async def no_org():
            raise OrganizationRequiredError()

        app.dependency_overrides[get_current_user] = no_org
        resp = await self.client.get("/links")
        assert resp.status_code == 403
