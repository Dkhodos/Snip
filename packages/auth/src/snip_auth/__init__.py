"""snip-auth: shared authentication client package."""

from snip_auth.exceptions import AuthenticationError, OrganizationRequiredError
from snip_auth.factory import create_auth_client
from snip_auth.protocol import AuthClient, AuthUser
from snip_auth.provider import AuthProvider

__all__ = [
    "AuthClient",
    "AuthProvider",
    "AuthUser",
    "AuthenticationError",
    "OrganizationRequiredError",
    "create_auth_client",
]
