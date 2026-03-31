"""Tests for get_current_user dependency."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from snip_auth import AuthenticationError, AuthUser
from snip_auth.providers.clerk.client import ClerkClient
from snip_auth.providers.dev.client import DevAuthClient

from dashboard_backend.dependencies import get_current_user


class TestGetCurrentUser:
    @patch("dashboard_backend.dependencies._is_dev_bypass", return_value=True)
    async def test_dev_bypass(self, _mock_bypass) -> None:
        client = DevAuthClient()
        request = MagicMock()
        user = await get_current_user(request, client)
        assert user == AuthUser(user_id="dev_user", org_id="dev_org")

    @patch("dashboard_backend.dependencies._is_dev_bypass", return_value=False)
    async def test_missing_auth_header(self, _mock_bypass) -> None:
        client = ClerkClient("pk_test_abc")
        request = MagicMock()
        request.headers.get.return_value = ""
        with pytest.raises(AuthenticationError, match="Missing"):
            await get_current_user(request, client)

    @patch("dashboard_backend.dependencies._is_dev_bypass", return_value=False)
    async def test_no_bearer_prefix(self, _mock_bypass) -> None:
        client = ClerkClient("pk_test_abc")
        request = MagicMock()
        request.headers.get.return_value = "Basic abc123"
        with pytest.raises(AuthenticationError, match="Missing"):
            await get_current_user(request, client)

    @patch("dashboard_backend.dependencies._is_dev_bypass", return_value=False)
    async def test_valid_token(self, _mock_bypass) -> None:
        client = AsyncMock()
        client.verify_token.return_value = AuthUser(user_id="u1", org_id="o1")
        request = MagicMock()
        request.headers.get.return_value = "Bearer valid_token"
        user = await get_current_user(request, client)
        assert user.user_id == "u1"
        client.verify_token.assert_called_once_with("valid_token")
