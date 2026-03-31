"""Tests for store factory dependencies."""

from unittest.mock import MagicMock

from snip_db.stores.click_event_store import ClickEventStore
from snip_db.stores.feature_flag_store import FeatureFlagStore
from snip_db.stores.link_store import LinkStore

from dashboard_backend.dependencies import (
    get_click_event_store,
    get_feature_flag_store,
    get_link_store,
)


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
