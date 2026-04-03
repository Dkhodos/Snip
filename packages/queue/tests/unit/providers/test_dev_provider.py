"""Tests for the dev queue publisher."""

import logging

import pytest

from snip_queue.providers.dev.client import DevQueuePublisher


@pytest.fixture
def publisher() -> DevQueuePublisher:
    return DevQueuePublisher()


class TestDevQueuePublisher:
    async def test_publish_returns_message_id(self, publisher: DevQueuePublisher) -> None:
        result = await publisher.publish("test-topic", b'{"key": "value"}')
        assert result.startswith("dev_")

    async def test_publish_logs_message(
        self, publisher: DevQueuePublisher, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO):
            await publisher.publish("click-events", b'{"event": "click"}')

        assert "message_published" in caplog.text
        assert "click-events" in caplog.text

    async def test_publish_tracks_messages(self, publisher: DevQueuePublisher) -> None:
        data = b'{"key": "value"}'
        attrs = {"type": "click"}
        await publisher.publish("topic-1", data, attributes=attrs)

        assert len(publisher.published) == 1
        assert publisher.published[0] == ("topic-1", data, attrs)

    async def test_publish_multiple_messages(self, publisher: DevQueuePublisher) -> None:
        await publisher.publish("t1", b"a")
        await publisher.publish("t2", b"b")
        await publisher.publish("t1", b"c")

        assert len(publisher.published) == 3

    async def test_publish_without_attributes(self, publisher: DevQueuePublisher) -> None:
        await publisher.publish("topic", b"data")
        assert publisher.published[0][2] is None
