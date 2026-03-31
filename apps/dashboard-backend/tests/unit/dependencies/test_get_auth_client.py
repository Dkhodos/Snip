"""Tests for get_auth_client dependency."""

from unittest.mock import patch

from snip_auth.providers.clerk.client import ClerkClient
from snip_auth.providers.dev.client import DevAuthClient

from dashboard_backend.dependencies import get_auth_client


class TestGetAuthClient:
    @patch("dashboard_backend.dependencies.settings")
    def test_dev_bypass(self, mock_settings) -> None:
        mock_settings.environment = "development"
        mock_settings.clerk_secret_key = "sk_test_..."
        client = get_auth_client()
        assert isinstance(client, DevAuthClient)

    @patch("dashboard_backend.dependencies.settings")
    def test_dev_bypass_empty_key(self, mock_settings) -> None:
        mock_settings.environment = "development"
        mock_settings.clerk_secret_key = ""
        client = get_auth_client()
        assert isinstance(client, DevAuthClient)

    @patch("dashboard_backend.dependencies.settings")
    def test_real_client(self, mock_settings) -> None:
        mock_settings.environment = "development"
        mock_settings.clerk_secret_key = "sk_test_realkey123"
        mock_settings.clerk_publishable_key = "pk_test_abc"
        client = get_auth_client()
        assert isinstance(client, ClerkClient)

    @patch("dashboard_backend.dependencies.settings")
    def test_production(self, mock_settings) -> None:
        mock_settings.environment = "production"
        mock_settings.clerk_secret_key = "sk_live_realkey"
        mock_settings.clerk_publishable_key = "pk_live_abc"
        client = get_auth_client()
        assert isinstance(client, ClerkClient)
