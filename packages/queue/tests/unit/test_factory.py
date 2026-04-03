"""Tests for the queue publisher factory."""

import pytest

from snip_queue.factory import create_queue_publisher
from snip_queue.provider import QueueProvider
from snip_queue.providers.dev.client import DevQueuePublisher


class TestCreateQueuePublisher:
    def test_dev_provider_returns_dev_publisher(self) -> None:
        publisher = create_queue_publisher(QueueProvider.DEV)
        assert isinstance(publisher, DevQueuePublisher)

    def test_gcp_pubsub_without_project_id_raises(self) -> None:
        with pytest.raises(ValueError, match="project_id"):
            create_queue_publisher(QueueProvider.GCP_PUBSUB, project_id="")

    def test_default_provider_is_gcp_pubsub_and_requires_project_id(self) -> None:
        with pytest.raises(ValueError, match="project_id"):
            create_queue_publisher()

    def test_default_provider_is_gcp_pubsub(self) -> None:
        with pytest.raises(ValueError, match="project_id"):
            create_queue_publisher(project_id="")
