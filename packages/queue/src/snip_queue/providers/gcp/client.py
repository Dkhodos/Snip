"""Google Cloud Pub/Sub publisher."""

import logging

from google.cloud import pubsub_v1

from snip_queue.protocol import QueuePublisher

_log = logging.getLogger(__name__)


class GcpPubSubPublisher:
    """Queue publisher backed by Google Cloud Pub/Sub."""

    def __init__(self, project_id: str) -> None:
        self._project_id = project_id
        self._client = pubsub_v1.PublisherClient()

    async def publish(
        self, topic: str, data: bytes, *, attributes: dict[str, str] | None = None
    ) -> str:
        """Publish a message to a Pub/Sub topic.

        Note: The google-cloud-pubsub library's publish() is synchronous but non-blocking
        (returns a future). We resolve it here for the async interface.
        """
        topic_path = self._client.topic_path(self._project_id, topic)
        future = self._client.publish(topic_path, data, **(attributes or {}))
        message_id = future.result()
        _log.info(f"message_published topic={topic} message_id={message_id}")
        return message_id


def _assert_implements_protocol() -> None:
    _: QueuePublisher = GcpPubSubPublisher(project_id="test")  # noqa: F841
