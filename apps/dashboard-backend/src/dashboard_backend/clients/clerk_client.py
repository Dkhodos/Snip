"""Clerk authentication client with swappable implementations."""

import base64
from dataclasses import dataclass
from typing import Protocol

import httpx
from jose import JWTError, jwt

from dashboard_backend.exceptions import AuthenticationError, OrganizationRequiredError


@dataclass(frozen=True)
class ClerkUser:
    user_id: str
    org_id: str


class AuthClient(Protocol):
    """Protocol for authentication clients."""

    async def verify_token(self, token: str) -> ClerkUser: ...


class ClerkClient:
    """Real Clerk JWT verification client."""

    def __init__(self, publishable_key: str) -> None:
        self._publishable_key = publishable_key
        self._jwks_cache: dict | None = None

    def _get_jwks_url(self) -> str:
        encoded = self._publishable_key.split("_", 2)[-1]
        padded = encoded + "=" * (-len(encoded) % 4)
        frontend_api = base64.b64decode(padded).decode().rstrip("$")
        return f"https://{frontend_api}/.well-known/jwks.json"

    async def _get_jwks(self) -> dict:
        if self._jwks_cache is None:
            url = self._get_jwks_url()
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)
                resp.raise_for_status()
                self._jwks_cache = resp.json()
        return self._jwks_cache

    async def verify_token(self, token: str) -> ClerkUser:
        try:
            jwks = await self._get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            key = None
            for k in jwks.get("keys", []):
                if k["kid"] == unverified_header.get("kid"):
                    key = k
                    break

            if key is None:
                raise AuthenticationError("Invalid token signing key")

            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )

            user_id = payload.get("sub", "")
            org_id = payload.get("org_id", "")

            if not user_id:
                raise AuthenticationError("Invalid token: missing user ID")

            if not org_id:
                raise OrganizationRequiredError()

            return ClerkUser(user_id=user_id, org_id=org_id)

        except (JWTError, AuthenticationError, OrganizationRequiredError):
            raise
        except Exception as e:
            raise AuthenticationError(f"Invalid token: {e}") from e


class DevAuthClient:
    """Dev bypass client that always returns a fixed user."""

    async def verify_token(self, token: str) -> ClerkUser:
        return ClerkUser(user_id="dev_user", org_id="dev_org")
