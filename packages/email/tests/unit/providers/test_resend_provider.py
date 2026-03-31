"""Tests for the Resend email provider."""

from unittest.mock import AsyncMock, patch

import pytest

from snip_email.protocol import EmailMessage
from snip_email.providers.resend.client import ResendClient


@pytest.fixture
def client() -> ResendClient:
    return ResendClient(api_key="re_test_123", from_email="Snip <noreply@snip.dev>")


@pytest.fixture
def message() -> EmailMessage:
    return EmailMessage(
        to=["user@example.com"],
        subject="Test Subject",
        html="<p>Hello</p>",
    )


class TestResendClient:
    async def test_send_calls_resend_api(self, client: ResendClient, message: EmailMessage) -> None:
        fake_response = {"id": "msg_abc123"}
        with patch("resend.Emails.send_async", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = fake_response
            result = await client.send(message)

        assert result == "msg_abc123"
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args["to"] == ["user@example.com"]
        assert call_args["subject"] == "Test Subject"
        assert call_args["html"] == "<p>Hello</p>"
        assert call_args["from"] == "Snip <noreply@snip.dev>"

    async def test_send_sets_api_key(self, client: ResendClient, message: EmailMessage) -> None:
        fake_response = {"id": "msg_123"}
        with (
            patch("resend.Emails.send_async", new_callable=AsyncMock, return_value=fake_response),
            patch("snip_email.providers.resend.client.resend") as mock_resend,
        ):
            mock_resend.Emails.send_async = AsyncMock(return_value=fake_response)
            await client.send(message)
            assert mock_resend.api_key == "re_test_123"

    async def test_send_returns_none_when_no_response(
        self, client: ResendClient, message: EmailMessage
    ) -> None:
        with patch("resend.Emails.send_async", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = None
            result = await client.send(message)

        assert result is None
