"""Tests for link input validation — target_url scheme and custom_short_code constraints."""

import pytest

from dashboard_backend.dependencies import get_link_manager
from tests.unit.base.base_api_test import BaseApiTestCase, make_link


class TestTargetUrlValidation(BaseApiTestCase):
    """CRIT-2: Only http/https URLs must be accepted for target_url."""

    @pytest.mark.parametrize(
        "url",
        [
            "javascript:alert(1)",
            "javascript:void(0)",
            "data:text/html,<script>alert(1)</script>",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "vbscript:msgbox(1)",
            "ftp://example.com/file.txt",
            "file:///etc/passwd",
            "//evil.com",
        ],
    )
    async def test_create_rejects_disallowed_scheme(self, url: str) -> None:
        self.override_user()
        self.override_manager(get_link_manager)
        resp = await self.client.post(
            "/links",
            json={"target_url": url, "title": "Test"},
        )
        assert resp.status_code == 422, f"Expected 422 for URL: {url!r}, got {resp.status_code}"

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "https://example.com/path?q=1#anchor",
            "http://localhost",
            "http://localhost:3000/dev",
            "https://sub.domain.example.com",
        ],
    )
    async def test_create_accepts_http_https(self, url: str) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.create_link.return_value = make_link(target_url=url)
        resp = await self.client.post(
            "/links",
            json={"target_url": url, "title": "Test"},
        )
        assert resp.status_code == 201, f"Expected 201 for URL: {url!r}, got {resp.status_code}"

    @pytest.mark.parametrize(
        "url",
        [
            "javascript:alert(1)",
            "data:text/html,<script>",
            "ftp://files.example.com",
        ],
    )
    async def test_update_rejects_disallowed_scheme(self, url: str) -> None:
        self.override_user()
        self.override_manager(get_link_manager)
        link = make_link()
        resp = await self.client.patch(
            f"/links/{link.id}",
            json={"target_url": url},
        )
        assert resp.status_code == 422, f"Expected 422 for URL: {url!r}, got {resp.status_code}"

    async def test_update_accepts_valid_url(self) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        link = make_link()
        mgr.update_link.return_value = link
        resp = await self.client.patch(
            f"/links/{link.id}",
            json={"target_url": "https://updated.example.com"},
        )
        assert resp.status_code == 200

    async def test_update_allows_null_target_url(self) -> None:
        """Omitting target_url from a PATCH is fine — field is optional."""
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        link = make_link()
        mgr.update_link.return_value = link
        resp = await self.client.patch(
            f"/links/{link.id}",
            json={"title": "New Title"},
        )
        assert resp.status_code == 200


class TestCustomShortCodeValidation(BaseApiTestCase):
    """HIGH-4: custom_short_code must match ^[a-zA-Z0-9_-]+$ and be 3-32 chars."""

    @pytest.mark.parametrize(
        "code",
        [
            "../etc/passwd",  # path traversal
            "hello world",  # space
            "code!",  # special char
            "a\x00b",  # null byte
            "",  # empty string
            "AB",  # too short (< 3)
            "a" * 33,  # too long (> 32)
        ],
    )
    async def test_create_rejects_invalid_short_code(self, code: str) -> None:
        self.override_user()
        self.override_manager(get_link_manager)
        resp = await self.client.post(
            "/links",
            json={"target_url": "https://example.com", "title": "Test", "custom_short_code": code},
        )
        assert resp.status_code == 422, f"Expected 422 for code: {code!r}, got {resp.status_code}"

    @pytest.mark.parametrize(
        "code",
        [
            "abc",
            "hello-world",
            "hello_world",
            "HelloWorld123",
            "a" * 32,  # exactly at max
            "abc",  # exactly at min
        ],
    )
    async def test_create_accepts_valid_short_code(self, code: str) -> None:
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.create_link.return_value = make_link()
        resp = await self.client.post(
            "/links",
            json={
                "target_url": "https://example.com",
                "title": "Test",
                "custom_short_code": code,
            },
        )
        assert resp.status_code == 201, f"Expected 201 for code: {code!r}, got {resp.status_code}"

    async def test_create_accepts_null_short_code(self) -> None:
        """Omitting custom_short_code is valid — auto-generated."""
        self.override_user()
        mgr = self.override_manager(get_link_manager)
        mgr.create_link.return_value = make_link()
        resp = await self.client.post(
            "/links",
            json={"target_url": "https://example.com", "title": "Test"},
        )
        assert resp.status_code == 201
