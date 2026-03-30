"""Feature flag data access store."""

from typing import List

from snip_db.models import FeatureFlag

from dashboard_backend.stores.base_store import BaseStore


class FeatureFlagStore(BaseStore[FeatureFlag]):
    model = FeatureFlag

    async def get_all(self) -> List[FeatureFlag]:
        return await self._get_all()
