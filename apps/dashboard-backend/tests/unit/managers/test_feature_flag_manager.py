"""Tests for FeatureFlagManager."""

from unittest.mock import AsyncMock

from snip_db.models import FeatureFlag

from dashboard_backend.managers import feature_flag_manager as ffm_module
from dashboard_backend.managers.feature_flag_manager import FeatureFlagManager


def _make_flag(key: str, enabled: bool) -> FeatureFlag:
    return FeatureFlag(key=key, enabled=enabled)


class TestFeatureFlagManager:
    def setup_method(self) -> None:
        # Reset module-level cache between tests
        ffm_module._flags_cache = None
        ffm_module._flags_cache_time = 0.0

    async def test_get_all_flags(self) -> None:
        store = AsyncMock()
        store.get_all.return_value = [
            _make_flag("flag_a", True),
            _make_flag("flag_b", False),
        ]

        manager = FeatureFlagManager(store)
        flags = await manager.get_all_flags()

        assert flags == {"flag_a": True, "flag_b": False}
        store.get_all.assert_called_once()

    async def test_cache_hit(self) -> None:
        store = AsyncMock()
        store.get_all.return_value = [_make_flag("x", True)]

        manager = FeatureFlagManager(store)
        await manager.get_all_flags()
        await manager.get_all_flags()

        # Only one DB call despite two manager calls
        store.get_all.assert_called_once()

    async def test_cache_expired(self) -> None:
        store = AsyncMock()
        store.get_all.return_value = [_make_flag("x", True)]

        manager = FeatureFlagManager(store)
        await manager.get_all_flags()

        # Expire cache
        ffm_module._flags_cache_time = 0.0

        await manager.get_all_flags()
        assert store.get_all.call_count == 2
