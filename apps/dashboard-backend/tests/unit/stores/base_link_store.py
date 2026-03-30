"""Shared helpers for LinkStore tests."""

from dashboard_backend.stores.link_store import LinkStore


async def create_link(store: LinkStore, **overrides) -> object:
    """Create a link with sensible defaults, accepting overrides."""
    defaults = {
        "org_id": "org1",
        "short_code": "abc123",
        "target_url": "https://example.com",
        "title": "Test",
        "created_by": "user1",
    }
    defaults.update(overrides)
    return await store.create(**defaults)
