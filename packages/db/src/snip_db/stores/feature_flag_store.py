"""Feature flag data access store."""

import logging
from typing import List

from snip_db.models import FeatureFlag
from snip_db.stores.base_store import BaseStore

_log = logging.getLogger(__name__)


class FeatureFlagStore(BaseStore[FeatureFlag]):
    model = FeatureFlag

    async def get_all(self) -> List[FeatureFlag]:
        flags = await self._get_all()
        _log.debug("feature_flags_fetched count=%d", len(flags))
        return flags
