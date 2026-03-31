"""Auth client factory."""

from snip_auth.protocol import AuthClient
from snip_auth.provider import AuthProvider
from snip_auth.providers.clerk.client import ClerkClient
from snip_auth.providers.dev.client import DevAuthClient


def create_auth_client(
    provider: AuthProvider = AuthProvider.CLERK,
    *,
    publishable_key: str = "",
) -> AuthClient:
    """Create an auth client for the given provider.

    For CLERK, ``publishable_key`` is required.
    For DEV, no configuration is needed.
    """
    if provider == AuthProvider.DEV:
        return DevAuthClient()

    if provider == AuthProvider.CLERK:
        if not publishable_key:
            msg = "CLERK provider requires a non-empty publishable_key"
            raise ValueError(msg)
        return ClerkClient(publishable_key)

    msg = f"Unsupported auth provider: {provider}"
    raise ValueError(msg)
