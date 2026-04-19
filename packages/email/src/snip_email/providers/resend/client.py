"""Resend email provider."""

import logging
from typing import Any

import resend

from snip_email.protocol import EmailClient, EmailMessage

_log = logging.getLogger(__name__)


class ResendClient:
    """Email client backed by the Resend API."""

    def __init__(self, api_key: str, from_email: str) -> None:
        self._api_key = api_key
        self._from_email = from_email

    async def send(self, message: EmailMessage) -> str | None:
        resend.api_key = self._api_key
        params: Any = {
            "from": self._from_email,
            "to": message.to,
            "subject": message.subject,
            "html": message.html,
        }
        response: Any = await resend.Emails.send_async(params)
        email_id = response["id"] if response else None
        _log.info(
            "email_sent provider=resend to=%s subject=%s id=%s",
            message.to,
            message.subject,
            email_id,
        )
        return email_id


def _assert_implements_protocol() -> None:
    """Compile-time check that ResendClient satisfies EmailClient."""
    _: EmailClient = ResendClient(api_key="", from_email="")  # noqa: F841
