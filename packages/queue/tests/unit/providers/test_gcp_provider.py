"""Tests for the GCP Pub/Sub publisher."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from snip_queue.providers.gcp.client import GcpPubSubPublisher


class TestGcpPubSubPublisher:
    @patch("snip_queue.providers.gcp.client.pubsub_v1.PublisherClient")
    async def test_publish_calls_pubsub(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.topic_path.return_value = "projects/test/topics/my-topic"
        mock_future = MagicMock()
        mock_future.result.return_value = "msg_123"
        mock_client.publish.return_value = mock_future

        publisher = GcpPubSubPublisher(project_id="test")
        result = await publisher.publish("my-topic", b'{"key": "value"}')

        assert result == "msg_123"
        mock_client.topic_path.assert_called_once_with("test", "my-topic")
        mock_client.publish.assert_called_once_with(
            "projects/test/topics/my-topic", b'{"key": "value"}'
        )

    @patch("snip_queue.providers.gcp.client.pubsub_v1.PublisherClient")
    async def test_publish_with_attributes(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.topic_path.return_value = "projects/test/topics/t"
        mock_future = MagicMock()
        mock_future.result.return_value = "msg_456"
        mock_client.publish.return_value = mock_future

        publisher = GcpPubSubPublisher(project_id="test")
        result = await publisher.publish("t", b"data", attributes={"key": "val"})

        assert result == "msg_456"
        mock_client.publish.assert_called_once_with("projects/test/topics/t", b"data", key="val")

    @patch("snip_queue.providers.gcp.client.pubsub_v1.PublisherClient")
    async def test_publish_logs_on_success(
        self, mock_client_cls: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.topic_path.return_value = "projects/test/topics/t"
        mock_future = MagicMock()
        mock_future.result.return_value = "msg_789"
        mock_client.publish.return_value = mock_future

        publisher = GcpPubSubPublisher(project_id="test")
        with caplog.at_level(logging.INFO):
            await publisher.publish("t", b"data")

        assert "message_published" in caplog.text
        assert "msg_789" in caplog.text
