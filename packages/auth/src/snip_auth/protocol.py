"""Auth client protocol and user types."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthUser:
    """Immutable authenticated user DTO."""

    user_id: str
    org_id: str


class AuthClient(Protocol):
    """Protocol for authentication clients."""

    async def verify_token(self, token: str) -> AuthUser: ...
