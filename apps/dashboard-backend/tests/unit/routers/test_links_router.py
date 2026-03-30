"""Tests for the links router."""

from dashboard_backend.dependencies import get_link_manager
from tests.unit.base.base_api_test import BaseApiTestCase, make_link


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
