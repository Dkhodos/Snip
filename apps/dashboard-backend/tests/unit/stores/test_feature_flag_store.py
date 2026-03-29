"""Tests for FeatureFlagStore."""

from snip_db.models import FeatureFlag

from dashboard_backend.stores.feature_flag_store import FeatureFlagStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestFeatureFlagStore(BaseDBTestCase):
    async def test_get_all_empty(self) -> None:
        store = FeatureFlagStore(self.session)
        flags = await store.get_all()
        assert flags == []

    async def test_get_all_with_data(self) -> None:
        self.session.add(FeatureFlag(key="flag_a", enabled=True, description="A"))
        self.session.add(FeatureFlag(key="flag_b", enabled=False, description="B"))
        await self.session.flush()

        store = FeatureFlagStore(self.session)
        flags = await store.get_all()
        assert len(flags) == 2
        keys = {f.key for f in flags}
        assert keys == {"flag_a", "flag_b"}
