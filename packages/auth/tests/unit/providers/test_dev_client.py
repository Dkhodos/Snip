"""Tests for DevAuthClient."""

from snip_auth.protocol import AuthUser
from snip_auth.providers.dev.client import DevAuthClient


class TestDevAuthClient:
    async def test_always_returns_dev_user(self) -> None:
        client = DevAuthClient()
        user = await client.verify_token("anything")
        assert user == AuthUser(user_id="dev_user", org_id="dev_org")

    async def test_empty_token(self) -> None:
        client = DevAuthClient()
        user = await client.verify_token("")
        assert user.user_id == "dev_user"
