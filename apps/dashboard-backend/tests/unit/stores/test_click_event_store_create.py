"""Tests for ClickEventStore create operations."""

from datetime import datetime
from uuid import uuid4

from dashboard_backend.stores.click_event_store import ClickEventStore
from tests.unit.base.base_test_case import BaseDBTestCase
from tests.unit.stores.base_click_event import make_link


class TestClickEventStoreCreate(BaseDBTestCase):
    async def test_create_event(self) -> None:
        link = await make_link(self.session)
        store = ClickEventStore(self.session)
        now = datetime.utcnow()
        event = await store.create(link_id=link.id, clicked_at=now)
        assert event.link_id == link.id
        assert event.clicked_at == now
        assert event.user_agent is None

    async def test_create_event_with_metadata(self) -> None:
        link = await make_link(self.session)
        store = ClickEventStore(self.session)
        event_id = uuid4()
        event = await store.create(
            event_id=event_id,
            link_id=link.id,
            clicked_at=datetime.utcnow(),
            user_agent="Mozilla/5.0",
            country="US",
        )
        assert event.id == event_id
        assert event.user_agent == "Mozilla/5.0"
        assert event.country == "US"
