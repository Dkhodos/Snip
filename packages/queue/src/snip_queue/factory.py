"""Queue publisher factory."""

from snip_queue.protocol import QueuePublisher
from snip_queue.provider import QueueProvider
from snip_queue.providers.dev.client import DevQueuePublisher
from snip_queue.providers.gcp.client import GcpPubSubPublisher


def create_queue_publisher(
    provider: QueueProvider = QueueProvider.GCP_PUBSUB,
    *,
    project_id: str = "",
) -> QueuePublisher:
    """Create a queue publisher for the given provider."""
    if provider == QueueProvider.DEV:
        return DevQueuePublisher()

    if provider == QueueProvider.GCP_PUBSUB:
        if not project_id:
            msg = "GCP_PUBSUB provider requires a non-empty project_id"
            raise ValueError(msg)
        return GcpPubSubPublisher(project_id=project_id)

    msg = f"Unsupported queue provider: {provider}"
    raise ValueError(msg)
