"""Email client factory."""

from snip_email.protocol import EmailClient
from snip_email.provider import EmailProvider
from snip_email.providers.mailpit.client import MailpitClient
from snip_email.providers.resend.client import ResendClient


def create_email_client(
    provider: EmailProvider = EmailProvider.RESEND,
    *,
    api_key: str = "",
    from_email: str,
    smtp_host: str = "localhost",
    smtp_port: int = 1025,
) -> EmailClient:
    """Create an email client for the given provider.

    For RESEND, ``api_key`` is required.
    For MAILPIT, ``smtp_host`` and ``smtp_port`` configure the SMTP target.
    """
    if provider == EmailProvider.MAILPIT:
        return MailpitClient(from_email=from_email, host=smtp_host, port=smtp_port)

    if provider == EmailProvider.RESEND:
        if not api_key:
            msg = "RESEND provider requires a non-empty api_key"
            raise ValueError(msg)
        return ResendClient(api_key=api_key, from_email=from_email)

    msg = f"Unsupported email provider: {provider}"
    raise ValueError(msg)
