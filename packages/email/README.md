# snip-email

Async email sending with pluggable providers.

## Protocol

```python
class EmailClient(Protocol):
    async def send(self, message: EmailMessage) -> Optional[str]: ...
```

Returns the provider's message ID on success.

## Providers

| Provider | Usage |
|----------|-------|
| `RESEND` | Production — sends via Resend API |
| `MAILPIT` | Local dev — sends via SMTP to Mailpit (web UI at `localhost:8025`) |

## Usage

```python
from snip_email import create_email_client, EmailProvider, EmailMessage

client = create_email_client(EmailProvider.MAILPIT, from_email="noreply@snip.dev")
await client.send(EmailMessage(to=["user@example.com"], subject="Hello", html="<p>Hi</p>"))
```
