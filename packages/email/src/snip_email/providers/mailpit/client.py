"""Mailpit email provider for local development.

Mailpit captures emails via SMTP and exposes a web UI at http://localhost:8025.
SMTP default: localhost:1025.
"""

import logging
from email.message import EmailMessage as StdlibEmailMessage
from typing import Optional

import aiosmtplib

from snip_email.protocol import EmailClient, EmailMessage

logger = logging.getLogger(__name__)

_DEFAULT_SMTP_HOST = "localhost"
_DEFAULT_SMTP_PORT = 1025


class MailpitClient:
    """Email client that sends via SMTP to a local Mailpit instance."""

    def __init__(
        self,
        from_email: str,
        *,
        host: str = _DEFAULT_SMTP_HOST,
        port: int = _DEFAULT_SMTP_PORT,
    ) -> None:
        self._from_email = from_email
        self._host = host
        self._port = port

    async def send(self, message: EmailMessage) -> Optional[str]:
        msg = StdlibEmailMessage()
        msg["From"] = self._from_email
        msg["To"] = ", ".join(message.to)
        msg["Subject"] = message.subject
        msg.set_content(message.html, subtype="html")

        await aiosmtplib.send(
            msg,
            hostname=self._host,
            port=self._port,
            use_tls=False,
        )
        logger.info("email_sent provider=mailpit to=%s subject=%s", message.to, message.subject)
        return None


def _assert_implements_protocol() -> None:
    """Compile-time check that MailpitClient satisfies EmailClient."""
    _: EmailClient = MailpitClient(from_email="")  # noqa: F841
