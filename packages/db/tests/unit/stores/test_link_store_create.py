"""Tests for LinkStore.create."""

from datetime import datetime, timedelta
from uuid import uuid4

from snip_db.stores.link_store import LinkStore
from tests.unit.base.base_test_case import BaseDBTestCase


class TestLinkStoreCreate(BaseDBTestCase):
    async def test_create_link(self) -> None:
        store = LinkStore(self.session)
        link = await store.create(
            org_id="org1",
            short_code="abc123",
            target_url="https://example.com",
            title="Test Link",
            created_by="user1",
        )
        assert link.id is not None
        assert link.org_id == "org1"
        assert link.short_code == "abc123"
        assert link.target_url == "https://example.com"
        assert link.title == "Test Link"
        assert link.click_count == 0
        assert link.is_active is True

    async def test_create_with_optional_fields(self) -> None:
        store = LinkStore(self.session)
        link_id = uuid4()
        now = datetime.utcnow()
        expires = now + timedelta(days=30)

        link = await store.create(
            link_id=link_id,
            org_id="org1",
            short_code="xyz789",
            target_url="https://example.com",
            title="Full Link",
            created_by="user1",
            click_count=42,
            is_active=False,
            created_at=now,
            expires_at=expires,
        )
        assert link.id == link_id
        assert link.click_count == 42
        assert link.is_active is False
        assert link.expires_at == expires
