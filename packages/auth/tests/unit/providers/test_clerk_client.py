"""Tests for ClerkClient."""

from unittest.mock import AsyncMock, patch

import pytest

from snip_auth.exceptions import AuthenticationError, OrganizationRequiredError
from snip_auth.protocol import AuthUser
from snip_auth.providers.clerk.client import ClerkClient


class TestClerkClient:
    def test_jwks_url_derivation(self) -> None:
        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")
        url = client._get_jwks_url()
        assert url == "https://tidy-stinkbug-62.clerk.accounts.dev/.well-known/jwks.json"

    async def test_verify_token_missing_kid(self) -> None:
        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")
        client._jwks_cache = {"keys": [{"kid": "key1"}]}

        with patch("snip_auth.providers.clerk.client.jwt") as mock_jwt:
            mock_jwt.get_unverified_header.return_value = {"kid": "wrong_kid"}
            with pytest.raises(AuthenticationError, match="signing key"):
                await client.verify_token("fake_token")

    async def test_verify_token_missing_user_id(self) -> None:
        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")
        client._jwks_cache = {"keys": [{"kid": "key1"}]}

        with patch("snip_auth.providers.clerk.client.jwt") as mock_jwt:
            mock_jwt.get_unverified_header.return_value = {"kid": "key1"}
            mock_jwt.decode.return_value = {"sub": "", "org_id": "org1"}
            with pytest.raises(AuthenticationError, match="missing user ID"):
                await client.verify_token("fake_token")

    async def test_verify_token_missing_org_id(self) -> None:
        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")
        client._jwks_cache = {"keys": [{"kid": "key1"}]}

        with patch("snip_auth.providers.clerk.client.jwt") as mock_jwt:
            mock_jwt.get_unverified_header.return_value = {"kid": "key1"}
            mock_jwt.decode.return_value = {"sub": "user_123", "org_id": ""}
            with pytest.raises(OrganizationRequiredError):
                await client.verify_token("fake_token")

    async def test_verify_token_success(self) -> None:
        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")
        client._jwks_cache = {"keys": [{"kid": "key1"}]}

        with patch("snip_auth.providers.clerk.client.jwt") as mock_jwt:
            mock_jwt.get_unverified_header.return_value = {"kid": "key1"}
            mock_jwt.decode.return_value = {"sub": "user_123", "org_id": "org_456"}
            user = await client.verify_token("valid_token")
            assert user == AuthUser(user_id="user_123", org_id="org_456")

    async def test_verify_token_jwt_error(self) -> None:
        from jose import JWTError

        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")
        client._jwks_cache = {"keys": [{"kid": "key1"}]}

        with patch("snip_auth.providers.clerk.client.jwt") as mock_jwt:
            mock_jwt.get_unverified_header.side_effect = JWTError("bad token")
            mock_jwt.JWTError = JWTError
            with pytest.raises(JWTError):
                await client.verify_token("bad")

    async def test_verify_token_unexpected_error(self) -> None:
        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")
        client._jwks_cache = {"keys": [{"kid": "key1"}]}

        with patch("snip_auth.providers.clerk.client.jwt") as mock_jwt:
            mock_jwt.get_unverified_header.return_value = {"kid": "key1"}
            mock_jwt.decode.side_effect = ValueError("something weird")
            with pytest.raises(AuthenticationError, match="something weird"):
                await client.verify_token("bad")

    async def test_get_jwks_caches(self) -> None:
        client = ClerkClient("pk_test_dGlkeS1zdGlua2J1Zy02Mi5jbGVyay5hY2NvdW50cy5kZXYk")

        mock_resp = AsyncMock()
        mock_resp.json.return_value = {"keys": []}
        mock_resp.raise_for_status.return_value = None

        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_resp
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "snip_auth.providers.clerk.client.httpx.AsyncClient",
            return_value=mock_http_client,
        ):
            jwks1 = await client._get_jwks()
            jwks2 = await client._get_jwks()

        assert jwks1 is jwks2
        mock_http_client.get.assert_called_once()
