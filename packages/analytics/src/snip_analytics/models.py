"""Analytics data models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ClickEventRow:
    """Immutable click event row for analytics storage."""

    event_id: str
    link_id: str
    short_code: str
    org_id: str
    clicked_at: datetime
    user_agent: str | None = None
    country: str | None = None

    def to_bq_row(self) -> dict:
        """Convert to BigQuery row dict."""
        return {
            "event_id": self.event_id,
            "link_id": self.link_id,
            "short_code": self.short_code,
            "org_id": self.org_id,
            "clicked_at": self.clicked_at.isoformat(),
            "user_agent": self.user_agent,
            "country": self.country,
            "ingested_at": datetime.now(tz=datetime.now().astimezone().tzinfo).isoformat(),
        }


@dataclass(frozen=True)
class DailyClickCount:
    """Click count for a single day."""

    date: str
    count: int
