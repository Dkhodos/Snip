"""Tests for LinkStore stats operations."""

from datetime import datetime, timedelta

from snip_db.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestLinkStoreStats(BaseDBTestCase):
    async def test_get_stats(self) -> None:
        store = LinkStore(self.session)
        # Active link
        await store.create(
            org_id="org1",
            short_code="s1",
            target_url="https://a.com",
            title="A",
            created_by="u",
            click_count=10,
        )
        # Inactive link
        await store.create(
            org_id="org1",
            short_code="s2",
            target_url="https://b.com",
            title="B",
            created_by="u",
            is_active=False,
            click_count=5,
        )
        # Expired link
        await store.create(
            org_id="org1",
            short_code="s3",
            target_url="https://c.com",
            title="C",
            created_by="u",
            click_count=3,
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        stats = await store.get_stats("org1")
        assert stats["total_links"] == 3
        assert stats["total_clicks"] == 18
        assert stats["active_links"] == 2  # s1 + s3 (expired but still is_active=True)
        assert stats["expired_links"] == 1
