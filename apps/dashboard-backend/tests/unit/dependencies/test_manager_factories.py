"""Tests for manager factory dependencies."""

from unittest.mock import MagicMock

from dashboard_backend.dependencies import (
    get_clicks_manager,
    get_feature_flag_manager,
    get_link_manager,
    get_redirect_manager,
    get_seed_manager,
)
from dashboard_backend.managers.clicks_manager import ClicksManager
from dashboard_backend.managers.feature_flag_manager import FeatureFlagManager
from dashboard_backend.managers.link_manager import LinkManager
from dashboard_backend.managers.redirect_manager import RedirectManager
from dashboard_backend.managers.seed_manager import SeedManager


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
