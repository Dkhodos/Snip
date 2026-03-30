"""Feature flag data access store."""

from __future__ import annotations

from snip_db.models import FeatureFlag

from dashboard_backend.stores.base_store import BaseStore


class FeatureFlagStore(BaseStore[FeatureFlag]):
    model = FeatureFlag

    async def get_all(self) -> list[FeatureFlag]:
        return await self._get_all()
