"""Tests for the email client factory."""

import pytest

from snip_email.factory import create_email_client
from snip_email.provider import EmailProvider
from snip_email.providers.mailpit.client import MailpitClient
from snip_email.providers.resend.client import ResendClient


class TestCreateEmailClient:
    def test_resend_provider_with_key_returns_resend_client(self) -> None:
        client = create_email_client(
            EmailProvider.RESEND, api_key="re_test_123", from_email="x@x.com"
        )
        assert isinstance(client, ResendClient)

    def test_default_provider_is_resend(self) -> None:
        client = create_email_client(api_key="re_test_123", from_email="x@x.com")
        assert isinstance(client, ResendClient)

    def test_resend_without_key_raises(self) -> None:
        with pytest.raises(ValueError, match="api_key"):
            create_email_client(EmailProvider.RESEND, api_key="", from_email="x@x.com")

    def test_mailpit_provider(self) -> None:
        client = create_email_client(EmailProvider.MAILPIT, from_email="x@x.com")
        assert isinstance(client, MailpitClient)

    def test_mailpit_with_custom_host_port(self) -> None:
        client = create_email_client(
            EmailProvider.MAILPIT, from_email="x@x.com", smtp_host="mail", smtp_port=2525
        )
        assert isinstance(client, MailpitClient)
        assert client._host == "mail"
        assert client._port == 2525
