"""snip-email: shared email client package."""

from snip_email.factory import create_email_client
from snip_email.protocol import EmailClient, EmailMessage
from snip_email.provider import EmailProvider

__all__ = [
    "EmailClient",
    "EmailMessage",
    "EmailProvider",
    "create_email_client",
]
