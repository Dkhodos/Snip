"""Tests for dependency injection wiring."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dashboard_backend.clients.clerk_client import ClerkClient, ClerkUser, DevAuthClient
from dashboard_backend.dependencies import (
    get_auth_client,
    get_click_event_store,
    get_clicks_manager,
    get_current_user,
    get_feature_flag_manager,
    get_feature_flag_store,
    get_link_manager,
    get_link_store,
    get_redirect_manager,
    get_seed_manager,
)
from dashboard_backend.exceptions import AuthenticationError
from dashboard_backend.managers.clicks_manager import ClicksManager
from dashboard_backend.managers.feature_flag_manager import FeatureFlagManager
from dashboard_backend.managers.link_manager import LinkManager
from dashboard_backend.managers.redirect_manager import RedirectManager
from dashboard_backend.managers.seed_manager import SeedManager
from dashboard_backend.stores.click_event_store import ClickEventStore
from dashboard_backend.stores.feature_flag_store import FeatureFlagStore
from dashboard_backend.stores.link_store import LinkStore


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


class TestGetCurrentUser:
    async def test_dev_bypass(self) -> None:
        client = DevAuthClient()
        request = MagicMock()
        user = await get_current_user(request, client)
        assert user == ClerkUser(user_id="dev_user", org_id="dev_org")

    async def test_missing_auth_header(self) -> None:
        client = ClerkClient("pk_test_abc")
        request = MagicMock()
        request.headers.get.return_value = ""
        with pytest.raises(AuthenticationError, match="Missing"):
            await get_current_user(request, client)

    async def test_no_bearer_prefix(self) -> None:
        client = ClerkClient("pk_test_abc")
        request = MagicMock()
        request.headers.get.return_value = "Basic abc123"
        with pytest.raises(AuthenticationError, match="Missing"):
            await get_current_user(request, client)

    async def test_valid_token(self) -> None:
        client = AsyncMock()
        client.verify_token.return_value = ClerkUser(user_id="u1", org_id="o1")
        request = MagicMock()
        request.headers.get.return_value = "Bearer valid_token"
        user = await get_current_user(request, client)
        assert user.user_id == "u1"
        client.verify_token.assert_called_once_with("valid_token")


class TestStoreFactories:
    def test_get_link_store(self) -> None:
        session = MagicMock()
        store = get_link_store(session)
        assert isinstance(store, LinkStore)

    def test_get_click_event_store(self) -> None:
        session = MagicMock()
        store = get_click_event_store(session)
        assert isinstance(store, ClickEventStore)

    def test_get_feature_flag_store(self) -> None:
        session = MagicMock()
        store = get_feature_flag_store(session)
        assert isinstance(store, FeatureFlagStore)


class TestManagerFactories:
    def test_get_link_manager(self) -> None:
        store = MagicMock()
        manager = get_link_manager(store)
        assert isinstance(manager, LinkManager)

    def test_get_redirect_manager(self) -> None:
        manager = get_redirect_manager(MagicMock(), MagicMock())
        assert isinstance(manager, RedirectManager)

    def test_get_clicks_manager(self) -> None:
        manager = get_clicks_manager(MagicMock(), MagicMock())
        assert isinstance(manager, ClicksManager)

    def test_get_feature_flag_manager(self) -> None:
        manager = get_feature_flag_manager(MagicMock())
        assert isinstance(manager, FeatureFlagManager)

    def test_get_seed_manager(self) -> None:
        manager = get_seed_manager(MagicMock(), MagicMock())
        assert isinstance(manager, SeedManager)
