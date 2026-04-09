---
name: provider-package-anatomy
description: Deep reference for building a shared package with the Provider Pattern — Protocol, StrEnum, Factory
---

# Provider Package Anatomy

Complete walkthrough of how shared packages are built, using the auth package as the canonical example.

## The Provider Pattern

```
External code  →  __init__.py (public API)  →  factory.py  →  providers/<impl>/client.py
                                                    ↑
                                              provider.py (StrEnum)
                                                    ↑
                                              protocol.py (interface)
```

The pattern decouples consumers from implementations. Apps choose a provider via config, and the factory returns the right client. In development, the `DEV` provider is used — no external services needed.

## 1. Protocol (`protocol.py`)

Defines the interface and DTOs:

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class AuthUser:
    """Immutable authenticated user DTO."""
    user_id: str
    org_id: str

class AuthClient(Protocol):
    async def verify_token(self, token: str) -> AuthUser: ...
```

**Key points:**
- DTOs are `@dataclass(frozen=True)` — always immutable
- Protocol defines the interface — implementations don't inherit from it
- Keep protocols minimal — only methods that all providers must support

## 2. Provider Enum (`provider.py`)

```python
from enum import StrEnum

class AuthProvider(StrEnum):
    CLERK = "clerk"
    DEV = "dev"
```

**Key points:**
- `StrEnum` so values match env var strings directly
- `DEV` is always present — local development must work without external services
- Values are lowercase

## 3. Factory (`factory.py`)

```python
from <project>_auth.protocol import AuthClient
from <project>_auth.provider import AuthProvider
from <project>_auth.providers.clerk.client import ClerkClient
from <project>_auth.providers.dev.client import DevAuthClient

def create_auth_client(
    provider: AuthProvider = AuthProvider.CLERK,
    *,
    publishable_key: str = "",
) -> AuthClient:
    if provider == AuthProvider.DEV:
        return DevAuthClient()
    if provider == AuthProvider.CLERK:
        if not publishable_key:
            raise ValueError("CLERK provider requires a non-empty publishable_key")
        return ClerkClient(publishable_key)
    raise ValueError(f"Unsupported auth provider: {provider}")
```

**Key points:**
- Return type is the Protocol, not the concrete class
- Provider-specific config via keyword-only args
- Validate required config per provider
- Raise `ValueError` for unknown providers

## 4. Dev Provider (`providers/dev/client.py`)

```python
from <project>_auth.protocol import AuthUser

class DevAuthClient:
    async def verify_token(self, token: str) -> AuthUser:
        return AuthUser(user_id="dev-user-001", org_id="dev-org-001")
```

**Key points:**
- Returns hardcoded values for local development
- No external dependencies
- Must satisfy the Protocol interface

## 5. Real Provider (`providers/clerk/client.py`)

```python
from <project>_auth.protocol import AuthUser
from <project>_auth.exceptions import AuthenticationError

class ClerkClient:
    def __init__(self, publishable_key: str) -> None:
        self._publishable_key = publishable_key

    async def verify_token(self, token: str) -> AuthUser:
        # Real implementation calling Clerk API
        ...
```

## 6. Public API (`__init__.py`)

```python
"""<project>-auth: shared authentication client package."""

from <project>_auth.exceptions import AuthenticationError, OrganizationRequiredError
from <project>_auth.factory import create_auth_client
from <project>_auth.protocol import AuthClient, AuthUser
from <project>_auth.provider import AuthProvider

__all__ = [
    "AuthClient",
    "AuthProvider",
    "AuthUser",
    "AuthenticationError",
    "OrganizationRequiredError",
    "create_auth_client",
]
```

**Key points:**
- Everything externally consumed is re-exported here
- Explicit `__all__` — no accidental exports
- External code imports `from <project>_auth import AuthClient, create_auth_client`
- Never import from submodules externally

## 7. How Apps Consume Packages

In the app's `dependencies.py`:

```python
from <project>_auth import AuthClient, AuthProvider, create_auth_client

def get_auth_client() -> AuthClient:
    if settings.environment == "development":
        return create_auth_client(AuthProvider.DEV)
    return create_auth_client(
        AuthProvider.CLERK,
        publishable_key=settings.clerk_publishable_key,
    )
```

Provider selection is driven by app config — the package doesn't know or care which environment it's running in.

## Packages Without Providers

Not every package needs the full Provider Pattern. The logger package is a utility package:

```
packages/logger/
  src/<project>_logger/
    __init__.py       # Public API
    logger.py         # get_logger(), configure_logging()
    middleware.py     # logging_middleware for FastAPI
```

Use the Provider Pattern when wrapping external services. Use a simpler structure for pure utility packages.
