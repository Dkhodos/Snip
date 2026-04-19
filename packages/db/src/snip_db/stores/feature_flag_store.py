"""Feature flag data access store."""

import logging

from snip_db.models import FeatureFlag
from snip_db.stores.base_store import BaseStore

_log = logging.getLogger(__name__)


class FeatureFlagStore(BaseStore[FeatureFlag]):
    model = FeatureFlag

    async def get_all(self) -> list[FeatureFlag]:
        flags = await self._get_all()
        _log.debug(f"feature_flags_fetched count={len(flags)}")
        return flags
