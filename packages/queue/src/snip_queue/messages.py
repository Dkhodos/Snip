"""Queue message types for click events."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

import orjson


@dataclass(frozen=True)
class ClickEventMessage:
    """Immutable click event message for queue publishing."""

    link_id: str
    short_code: str
    org_id: str
    clicked_at: datetime
    user_agent: str | None = None
    country: str | None = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_json(self) -> bytes:
        """Serialize to JSON bytes for queue publishing."""
        data = {
            "event_id": self.event_id,
            "link_id": self.link_id,
            "short_code": self.short_code,
            "org_id": self.org_id,
            "clicked_at": self.clicked_at.isoformat(),
            "user_agent": self.user_agent,
            "country": self.country,
        }
        return orjson.dumps(data)

    @classmethod
    def from_json(cls, data: bytes) -> ClickEventMessage:
        """Deserialize from JSON bytes."""
        parsed = orjson.loads(data)
        return cls(
            event_id=parsed["event_id"],
            link_id=parsed["link_id"],
            short_code=parsed["short_code"],
            org_id=parsed["org_id"],
            clicked_at=datetime.fromisoformat(parsed["clicked_at"]),
            user_agent=parsed.get("user_agent"),
            country=parsed.get("country"),
        )
