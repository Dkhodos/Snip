# snip-auth

JWT verification and user context extraction with pluggable providers.

## Protocol

```python
class AuthClient(Protocol):
    async def verify_token(self, token: str) -> AuthUser: ...
```

Returns `AuthUser(user_id, org_id)` on success, raises `AuthenticationError` or `OrganizationRequiredError` on failure.

## Providers

| Provider | Usage |
|----------|-------|
| `CLERK` | Production — verifies JWTs against Clerk's JWKS endpoint |
| `DEV` | Local dev — returns a fixed `dev_user` / `dev_org` for any token |

## Usage

```python
from snip_auth import create_auth_client, AuthProvider

client = create_auth_client(AuthProvider.CLERK, clerk_secret_key="sk_...")
user = await client.verify_token(bearer_token)
```
