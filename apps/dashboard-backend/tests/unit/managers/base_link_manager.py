"""Shared helpers for LinkManager tests."""

from uuid import uuid4

from snip_db.models import Link


def make_link(**overrides) -> Link:
    """Create a Link instance for test assertions."""
    defaults = {
        "id": uuid4(),
        "org_id": "org1",
        "short_code": "abc123",
        "target_url": "https://example.com",
        "title": "Test",
        "created_by": "user1",
        "click_count": 0,
        "is_active": True,
    }
    defaults.update(overrides)
    return Link(**defaults)
