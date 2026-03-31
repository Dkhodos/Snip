"""Base test case for API router tests.

Provides an async httpx client, auto-cleans dependency overrides,
and offers helpers to mock managers and override the authenticated user.

Usage:
    class TestLinksRouter(BaseApiTestCase):
        async def test_list(self) -> None:
            manager = self.override_manager(get_link_manager)
            manager.list_links.return_value = ([], 0)
            resp = await self.client.get("/links")
            assert resp.status_code == 200
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from snip_auth import AuthUser
from snip_db.models import Link

from dashboard_backend.dependencies import get_current_user
from dashboard_backend.main import app

TEST_USER = AuthUser(user_id="test_user", org_id="test_org")


def make_link(**overrides: Any) -> Link:
    """Create a Link instance for test assertions."""
    defaults = {
        "id": uuid4(),
        "org_id": "test_org",
        "short_code": "abc123",
        "target_url": "https://example.com",
        "title": "Test",
        "created_by": "test_user",
        "click_count": 0,
        "is_active": True,
        "created_at": datetime(2026, 1, 1),
        "expires_at": None,
    }
    defaults.update(overrides)
    return Link(**defaults)


class BaseApiTestCase:
    """Base class for router / API integration tests.

    Provides:
        - ``self.client`` — async httpx client hitting the FastAPI app
        - ``self.override_user(user)`` — set the authenticated user
        - ``self.override_manager(dep)`` — replace a manager dependency with AsyncMock
        - Automatic cleanup of all dependency overrides after each test
    """

    client: AsyncClient

    @pytest.fixture(autouse=True)
    async def _api_setup(self) -> None:
        # Clear any leftover overrides
        app.dependency_overrides.clear()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            self.client = c
            yield

        # Cleanup after each test
        app.dependency_overrides.clear()

    def override_user(self, user: AuthUser = TEST_USER) -> None:
        """Override the authenticated user for this test."""
        app.dependency_overrides[get_current_user] = lambda: user

    def override_manager(self, dependency: Callable) -> AsyncMock:
        """Replace a manager dependency with an AsyncMock and return it."""
        mock = AsyncMock()
        app.dependency_overrides[dependency] = lambda: mock
        return mock
