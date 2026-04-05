"""Tests for manager factory dependencies."""

from unittest.mock import MagicMock

from dashboard_backend.dependencies import (
    get_clicks_manager,
    get_feature_flag_manager,
    get_link_manager,
)
from dashboard_backend.managers.clicks_manager import ClicksManager
from dashboard_backend.managers.feature_flag_manager import FeatureFlagManager
from dashboard_backend.managers.link_manager import LinkManager


class TestManagerFactories:
    def test_get_link_manager(self) -> None:
        store = MagicMock()
        manager = get_link_manager(store)
        assert isinstance(manager, LinkManager)

    def test_get_clicks_manager(self) -> None:
        manager = get_clicks_manager(MagicMock(), MagicMock())
        assert isinstance(manager, ClicksManager)

    def test_get_feature_flag_manager(self) -> None:
        manager = get_feature_flag_manager(MagicMock())
        assert isinstance(manager, FeatureFlagManager)
