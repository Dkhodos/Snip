# Package Conventions (Shared Libraries)

Applies to: `packages/auth/`, `packages/db/`, `packages/email/`, `packages/logger/`, `packages/queue/`, `packages/analytics/`, `packages/storage/`, `packages/og-image/`

## Provider Pattern

Every package that wraps an external service follows the Provider Pattern:

```
packages/<name>/
  src/<project>_<name>/
    __init__.py        # Public API — explicit __all__ exports
    protocol.py        # typing.Protocol for the client interface
    provider.py        # StrEnum of supported providers
    factory.py         # create_<thing>_client() factory function
    exceptions.py      # Package-specific exceptions (optional)
    providers/
      dev/             # Local/test implementation (always present)
        __init__.py
        client.py
      <real>/          # Production implementation (clerk, resend, gcp, etc.)
        __init__.py
        client.py
```

Not all packages need all files (e.g., the logger package has no providers). Use this pattern when wrapping external services.

## Protocol (`protocol.py`)

Define the client interface as a `typing.Protocol`:

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class AuthUser:
    """Immutable DTO."""
    user_id: str
    org_id: str

class AuthClient(Protocol):
    async def verify_token(self, token: str) -> AuthUser: ...
```

- DTOs are `@dataclass(frozen=True)` — immutable
- Implementations follow the protocol without inheriting from it

## Provider Enum (`provider.py`)

```python
from enum import StrEnum

class AuthProvider(StrEnum):
    CLERK = "clerk"
    DEV = "dev"
```

- Always include a `DEV` variant for local development
- Use `StrEnum` so values can come directly from env vars / config

## Factory (`factory.py`)

```python
from <project>_auth.protocol import AuthClient
from <project>_auth.provider import AuthProvider

def create_auth_client(
    provider: AuthProvider = AuthProvider.CLERK,
    *,
    publishable_key: str = "",
) -> AuthClient:
    if provider == AuthProvider.DEV:
        return DevAuthClient()
    if provider == AuthProvider.CLERK:
        return ClerkClient(publishable_key)
    raise ValueError(f"Unsupported auth provider: {provider}")
```

- Returns the protocol type (not the concrete class)
- Provider-specific kwargs are keyword-only
- Raises `ValueError` for unknown providers

## Public API (`__init__.py`)

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

- **Everything** consumed externally is re-exported from `__init__.py`
- External code imports from `<project>_<name>`, never from submodules
- Explicit `__all__` list

## Naming

| Aspect | Convention | Example |
|--------|-----------|---------|
| pip name | `<project>-<name>` | `<project>-auth` |
| import name | `<project>_<name>` | `<project>_auth` |
| workspace source | `{ workspace = true }` | `<project>-auth = { workspace = true }` |
| directory | `packages/<name>/` | `packages/auth/` |
| src path | `src/<project>_<name>/` | `src/<project>_auth/` |

## pyproject.toml

```toml
[project]
name = "<project>-<name>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [...]

[tool.uv.sources]
# workspace references to other <project> packages

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Dev dependencies (pytest, ruff, pyright) are defined in the root `[dependency-groups] dev`. Only add a member-level `[dependency-groups] dev` if the package needs extra test-only deps beyond the common set (e.g., `aiosqlite` for database packages).

Same ruff and pyright config as apps (line-length 100, standard mode).

## Adding a New Package

1. Create `packages/<name>/` with the structure above
2. Add `"packages/<name>"` is already covered by `"packages/*"` in root `pyproject.toml` workspace members
3. Add `<project>-<name> = { workspace = true }` to consuming apps' `[tool.uv.sources]`
4. Run `uv sync --all-packages` from repo root
5. Create Makefile following the same pattern as other packages
6. Add project entry to root Makefile's `PROJECTS` list
