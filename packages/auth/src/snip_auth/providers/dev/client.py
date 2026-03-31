"""Dev authentication provider that skips real auth."""

from snip_auth.protocol import AuthClient, AuthUser


class DevAuthClient:
    """Dev bypass client that always returns a fixed user."""

    async def verify_token(self, token: str) -> AuthUser:
        return AuthUser(user_id="dev_user", org_id="dev_org")


def _assert_implements_protocol() -> None:
    """Compile-time check that DevAuthClient satisfies AuthClient."""
    _: AuthClient = DevAuthClient()  # noqa: F841
