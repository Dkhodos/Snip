"""Tests for queue message types."""

from datetime import UTC, datetime

import orjson

from snip_queue.messages import ClickEventMessage


class TestClickEventMessage:
    def test_roundtrip_serialization(self) -> None:
        now = datetime.now(tz=UTC)
        msg = ClickEventMessage(
            link_id="link_123",
            short_code="abc",
            org_id="org_456",
            clicked_at=now,
            user_agent="Mozilla/5.0",
            country="US",
        )

        data = msg.to_json()
        restored = ClickEventMessage.from_json(data)

        assert restored.link_id == msg.link_id
        assert restored.short_code == msg.short_code
        assert restored.org_id == msg.org_id
        assert restored.clicked_at == msg.clicked_at
        assert restored.user_agent == msg.user_agent
        assert restored.country == msg.country
        assert restored.event_id == msg.event_id

    def test_auto_generated_event_id(self) -> None:
        msg = ClickEventMessage(
            link_id="link_1",
            short_code="x",
            org_id="org_1",
            clicked_at=datetime.now(tz=UTC),
        )
        assert msg.event_id
        assert len(msg.event_id) == 36  # UUID format

    def test_none_fields_handled(self) -> None:
        now = datetime.now(tz=UTC)
        msg = ClickEventMessage(
            link_id="link_1",
            short_code="x",
            org_id="org_1",
            clicked_at=now,
        )

        data = msg.to_json()
        parsed = orjson.loads(data)
        assert parsed["user_agent"] is None
        assert parsed["country"] is None

        restored = ClickEventMessage.from_json(data)
        assert restored.user_agent is None
        assert restored.country is None

    def test_to_json_returns_bytes(self) -> None:
        msg = ClickEventMessage(
            link_id="link_1",
            short_code="x",
            org_id="org_1",
            clicked_at=datetime.now(tz=UTC),
        )
        assert isinstance(msg.to_json(), bytes)

    def test_frozen_dataclass(self) -> None:
        msg = ClickEventMessage(
            link_id="link_1",
            short_code="x",
            org_id="org_1",
            clicked_at=datetime.now(tz=UTC),
        )
        try:
            msg.link_id = "new_id"  # type: ignore[misc]
            raise AssertionError("Should have raised FrozenInstanceError")
        except AttributeError:
            pass
