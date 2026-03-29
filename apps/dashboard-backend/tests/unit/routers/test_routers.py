"""Integration tests for all routers."""

from unittest.mock import patch
from uuid import uuid4

from dashboard_backend.dependencies import (
    get_clicks_manager,
    get_current_user,
    get_feature_flag_manager,
    get_link_manager,
    get_redirect_manager,
    get_seed_manager,
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
from tests.unit.base.base_api_test import BaseApiTestCase, make_link

# --- Links ---


class TestLinksRouter(BaseApiTestCase):
    async def test_create_link(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.create_link.return_value = make_link()
        resp = await self.client.post(
            "/links",
            json={
                "target_url": "https://example.com",
                "title": "Test",
            },
        )
        assert resp.status_code == 201

    async def test_list_links(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.list_links.return_value = ([make_link()], 1)
        resp = await self.client.get("/links")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    async def test_get_link(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        link = make_link()
        mgr.get_link.return_value = link
        resp = await self.client.get(f"/links/{link.id}")
        assert resp.status_code == 200

    async def test_update_link(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        link = make_link()
        mgr.update_link.return_value = link
        resp = await self.client.patch(f"/links/{link.id}", json={"title": "New"})
        assert resp.status_code == 200

    async def test_delete_link(self) -> None:
        self.override_user()
        self.override_manager(get_link_manager)
        link = make_link()
        resp = await self.client.delete(f"/links/{link.id}")
        assert resp.status_code == 204


# --- Redirect ---


class TestRedirectRouter(BaseApiTestCase):
    async def test_redirect(self) -> None:
        mgr = self.override_manager(get_redirect_manager)
        mgr.resolve_redirect.return_value = "https://target.com"
        resp = await self.client.get("/r/abc123", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://target.com"


# --- Clicks ---


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


# --- Stats ---


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


# --- Flags ---


class TestFlagsRouter(BaseApiTestCase):
    async def test_get_flags(self) -> None:
        mgr = self.override_manager(get_feature_flag_manager)
        mgr.get_all_flags.return_value = {"flag_a": True}
        resp = await self.client.get("/flags")
        assert resp.status_code == 200
        assert resp.json() == {"flag_a": True}


# --- Health ---


class TestHealthRouter(BaseApiTestCase):
    async def test_health(self) -> None:
        resp = await self.client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# --- Seed ---


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


# --- Exception handlers ---


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
