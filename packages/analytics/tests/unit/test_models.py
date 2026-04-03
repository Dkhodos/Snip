"""Tests for analytics data models."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from snip_analytics.models import ClickEventRow, DailyClickCount


class TestClickEventRow:
    """Tests for ClickEventRow."""

    def test_to_bq_row_returns_correct_dict(self) -> None:
        clicked_at = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)
        event = ClickEventRow(
            event_id="evt-1",
            link_id="link-1",
            short_code="abc",
            org_id="org-1",
            clicked_at=clicked_at,
            user_agent="Mozilla/5.0",
            country="US",
        )
        row = event.to_bq_row()

        assert row["event_id"] == "evt-1"
        assert row["link_id"] == "link-1"
        assert row["short_code"] == "abc"
        assert row["org_id"] == "org-1"
        assert row["clicked_at"] == "2025-01-15T10:30:00+00:00"
        assert row["user_agent"] == "Mozilla/5.0"
        assert row["country"] == "US"
        assert "ingested_at" in row

    def test_to_bq_row_with_none_optional_fields(self) -> None:
        clicked_at = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)
        event = ClickEventRow(
            event_id="evt-2",
            link_id="link-2",
            short_code="xyz",
            org_id="org-2",
            clicked_at=clicked_at,
        )
        row = event.to_bq_row()

        assert row["user_agent"] is None
        assert row["country"] is None

    def test_click_event_row_is_frozen(self) -> None:
        clicked_at = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)
        event = ClickEventRow(
            event_id="evt-1",
            link_id="link-1",
            short_code="abc",
            org_id="org-1",
            clicked_at=clicked_at,
        )
        with pytest.raises(FrozenInstanceError):
            event.event_id = "changed"  # type: ignore[misc]


class TestDailyClickCount:
    """Tests for DailyClickCount."""

    def test_daily_click_count_is_frozen(self) -> None:
        count = DailyClickCount(date="2025-01-15", count=42)
        with pytest.raises(FrozenInstanceError):
            count.count = 99  # type: ignore[misc]

    def test_daily_click_count_fields(self) -> None:
        count = DailyClickCount(date="2025-01-15", count=42)
        assert count.date == "2025-01-15"
        assert count.count == 42
