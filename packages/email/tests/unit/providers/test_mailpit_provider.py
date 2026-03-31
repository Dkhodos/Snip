"""Tests for the Mailpit email provider."""

import logging
from unittest.mock import AsyncMock, patch

import pytest

from snip_email.protocol import EmailMessage
from snip_email.providers.mailpit.client import MailpitClient

_SEND_PATH = "snip_email.providers.mailpit.client.aiosmtplib.send"


class TestMailpitClient:
    async def test_send_calls_aiosmtplib(self) -> None:
        client = MailpitClient(from_email="test@snip.dev", host="localhost", port=1025)
        message = EmailMessage(
            to=["user@example.com"],
            subject="Test",
            html="<p>Hello</p>",
        )
        with patch(_SEND_PATH, new_callable=AsyncMock) as mock_send:
            result = await client.send(message)

        assert result is None
        mock_send.assert_called_once()
        kwargs = mock_send.call_args[1]
        assert kwargs["hostname"] == "localhost"
        assert kwargs["port"] == 1025
        assert kwargs["use_tls"] is False

    async def test_send_logs_on_success(self, caplog: pytest.LogCaptureFixture) -> None:
        client = MailpitClient(from_email="test@snip.dev")
        message = EmailMessage(to=["user@example.com"], subject="Log test", html="<p>Hi</p>")
        with (
            patch(_SEND_PATH, new_callable=AsyncMock),
            caplog.at_level(logging.INFO),
        ):
            await client.send(message)

        assert "Mailpit email sent" in caplog.text

    async def test_send_with_multiple_recipients(self) -> None:
        client = MailpitClient(from_email="test@snip.dev")
        message = EmailMessage(
            to=["a@example.com", "b@example.com"],
            subject="Multi",
            html="<p>Hi</p>",
        )
        with patch(_SEND_PATH, new_callable=AsyncMock) as mock_send:
            await client.send(message)

        sent_msg = mock_send.call_args[0][0]
        assert "a@example.com" in sent_msg["To"]
        assert "b@example.com" in sent_msg["To"]
