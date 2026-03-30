"""Feature flag business logic manager."""

from __future__ import annotations

import time

from dashboard_backend.stores.feature_flag_store import FeatureFlagStore

_CACHE_TTL = 60.0

# Class-level cache shared across all instances (survives per-request lifecycle)
_flags_cache: dict[str, bool] | None = None
_flags_cache_time: float = 0.0


class FeatureFlagManager:
    def __init__(self, feature_flag_store: FeatureFlagStore) -> None:
        self._store = feature_flag_store

    async def get_all_flags(self) -> dict[str, bool]:
        global _flags_cache, _flags_cache_time

        now = time.time()
        if _flags_cache is not None and (now - _flags_cache_time) < _CACHE_TTL:
            return _flags_cache

        flags = await self._store.get_all()
        _flags_cache = {flag.key: flag.enabled for flag in flags}
        _flags_cache_time = now

        return _flags_cache
