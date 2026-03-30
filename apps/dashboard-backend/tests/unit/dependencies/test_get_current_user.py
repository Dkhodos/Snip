"""Tests for get_current_user dependency."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from dashboard_backend.clients.clerk_client import ClerkClient, ClerkUser, DevAuthClient
from dashboard_backend.dependencies import get_current_user
from dashboard_backend.exceptions import AuthenticationError


class TestGetCurrentUser:
    async def test_dev_bypass(self) -> None:
        client = DevAuthClient()
        request = MagicMock()
        user = await get_current_user(request, client)
        assert user == ClerkUser(user_id="dev_user", org_id="dev_org")

    async def test_missing_auth_header(self) -> None:
        client = ClerkClient("pk_test_abc")
        request = MagicMock()
        request.headers.get.return_value = ""
        with pytest.raises(AuthenticationError, match="Missing"):
            await get_current_user(request, client)

    async def test_no_bearer_prefix(self) -> None:
        client = ClerkClient("pk_test_abc")
        request = MagicMock()
        request.headers.get.return_value = "Basic abc123"
        with pytest.raises(AuthenticationError, match="Missing"):
            await get_current_user(request, client)

    async def test_valid_token(self) -> None:
        client = AsyncMock()
        client.verify_token.return_value = ClerkUser(user_id="u1", org_id="o1")
        request = MagicMock()
        request.headers.get.return_value = "Bearer valid_token"
        user = await get_current_user(request, client)
        assert user.user_id == "u1"
        client.verify_token.assert_called_once_with("valid_token")
