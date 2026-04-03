"""Clerk authentication provider."""

import base64
import logging
from typing import Dict, Optional

import httpx
from jose import JWTError, jwt

from snip_auth.exceptions import AuthenticationError, OrganizationRequiredError
from snip_auth.protocol import AuthClient, AuthUser

_log = logging.getLogger(__name__)


class ClerkClient:
    """Real Clerk JWT verification client."""

    def __init__(self, publishable_key: str) -> None:
        self._publishable_key = publishable_key
        self._jwks_cache: Optional[Dict] = None

    def _get_jwks_url(self) -> str:
        encoded = self._publishable_key.split("_", 2)[-1]
        padded = encoded + "=" * (-len(encoded) % 4)
        frontend_api = base64.b64decode(padded).decode().rstrip("$")
        return f"https://{frontend_api}/.well-known/jwks.json"

    async def _get_jwks(self) -> Dict:
        if self._jwks_cache is None:
            url = self._get_jwks_url()
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)
                resp.raise_for_status()
                self._jwks_cache = resp.json()
            _log.info("jwks_fetched url=%s", self._get_jwks_url())
        assert self._jwks_cache is not None
        return self._jwks_cache

    async def verify_token(self, token: str) -> AuthUser:
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
            # Clerk JWT v2 uses "o.id"; v1 used top-level "org_id"
            org_claim = payload.get("o")
            if isinstance(org_claim, dict):
                org_id = org_claim.get("id", "")
            else:
                org_id = payload.get("org_id", "")

            if not user_id:
                raise AuthenticationError("Invalid token: missing user ID")

            if not org_id:
                raise OrganizationRequiredError()

            _log.info("token_verified user_id=%s org_id=%s", user_id, org_id)
            return AuthUser(user_id=user_id, org_id=org_id)

        except (JWTError, AuthenticationError, OrganizationRequiredError):
            raise
        except Exception as e:
            raise AuthenticationError(f"Invalid token: {e}") from e


def _assert_implements_protocol() -> None:
    """Compile-time check that ClerkClient satisfies AuthClient."""
    _: AuthClient = ClerkClient(publishable_key="")  # noqa: F841
