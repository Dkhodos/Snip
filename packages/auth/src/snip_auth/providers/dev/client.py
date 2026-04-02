"""Dev authentication provider that skips real auth."""

import logging

from snip_auth.protocol import AuthClient, AuthUser

_log = logging.getLogger(__name__)


class DevAuthClient:
    """Dev bypass client that always returns a fixed user."""

    async def verify_token(self, token: str) -> AuthUser:
        _log.info("dev_auth_bypass user_id=dev_user org_id=dev_org")
        return AuthUser(user_id="dev_user", org_id="dev_org")


def _assert_implements_protocol() -> None:
    """Compile-time check that DevAuthClient satisfies AuthClient."""
    _: AuthClient = DevAuthClient()  # noqa: F841
