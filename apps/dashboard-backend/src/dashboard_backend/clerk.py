"""Clerk JWT authentication middleware."""

from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt

from dashboard_backend.config import settings

_jwks_cache: dict | None = None


@dataclass
class ClerkUser:
    user_id: str
    org_id: str


async def _get_jwks() -> dict:
    """Fetch and cache Clerk JWKS."""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.clerk.dev/v1/jwks")
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


async def get_current_user(request: Request) -> ClerkUser:
    """FastAPI dependency: validate Clerk JWT and return current user."""
    # Dev bypass
    if settings.environment == "development":
        return ClerkUser(user_id="dev_user", org_id="dev_org")

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = auth_header.removeprefix("Bearer ")

    try:
        jwks = await _get_jwks()
        # Get the signing key
        unverified_header = jwt.get_unverified_header(token)
        key = None
        for k in jwks.get("keys", []):
            if k["kid"] == unverified_header.get("kid"):
                key = k
                break

        if key is None:
            raise HTTPException(status_code=401, detail="Invalid token signing key")

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )

        user_id = payload.get("sub", "")
        org_id = payload.get("org_id", "")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

        return ClerkUser(user_id=user_id, org_id=org_id)

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
