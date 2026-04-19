"""Dev email provider that logs instead of sending."""

import logging

from snip_email.protocol import EmailClient, EmailMessage

logger = logging.getLogger(__name__)


class DevEmailClient:
    """Dev bypass email client that logs messages instead of sending."""

    async def send(self, message: EmailMessage) -> str | None:
        logger.info(
            "email_sent provider=dev to=%s subject=%s",
            message.to,
            message.subject,
        )
        return "dev_email_id"


def _assert_implements_protocol() -> None:
    """Compile-time check that DevEmailClient satisfies EmailClient."""
    _: EmailClient = DevEmailClient()  # noqa: F841
