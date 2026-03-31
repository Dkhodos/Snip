"""Tests for the dev email provider."""

import logging

import pytest

from snip_email.protocol import EmailMessage
from snip_email.providers.dev.client import DevEmailClient


@pytest.fixture
def client() -> DevEmailClient:
    return DevEmailClient()


@pytest.fixture
def message() -> EmailMessage:
    return EmailMessage(
        to=["user@example.com"],
        subject="Test Subject",
        html="<p>Hello</p>",
    )


class TestDevEmailClient:
    async def test_send_returns_dev_id(self, client: DevEmailClient, message: EmailMessage) -> None:
        result = await client.send(message)
        assert result == "dev_email_id"

    async def test_send_logs_message(
        self, client: DevEmailClient, message: EmailMessage, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO):
            await client.send(message)

        assert "DEV EMAIL" in caplog.text
        assert "user@example.com" in caplog.text
        assert "Test Subject" in caplog.text

    async def test_send_with_multiple_recipients(self, client: DevEmailClient) -> None:
        message = EmailMessage(
            to=["a@example.com", "b@example.com"],
            subject="Multi",
            html="<p>Hi</p>",
        )
        result = await client.send(message)
        assert result == "dev_email_id"
