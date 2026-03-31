"""Shared helpers for ClickEventStore tests."""

from datetime import datetime, timedelta
from uuid import uuid4

from snip_db.stores.click_event_store import ClickEventStore
from snip_db.stores.link_store import LinkStore


async def make_link(session) -> object:
    """Create a link for use in click event tests."""
    store = LinkStore(session)
    return await store.create(
        org_id="org1",
        short_code=f"lnk{uuid4().hex[:6]}",
        target_url="https://example.com",
        title="Test",
        created_by="user1",
    )


async def seed_clicks(session) -> tuple:
    """Seed a link with click events spread over several days.

    Returns (link, click_store, now).
    """
    link_store = LinkStore(session)
    click_store = ClickEventStore(session)
    now = datetime.utcnow()

    link = await link_store.create(
        org_id="org1",
        short_code="qlink1",
        target_url="https://example.com",
        title="Query Link",
        created_by="user1",
    )

    # Create clicks over several days
    for day in range(5):
        for _ in range(day + 1):  # 1, 2, 3, 4, 5 clicks per day
            await click_store.create(
                link_id=link.id,
                clicked_at=now - timedelta(days=day),
            )

    return link, click_store, now
