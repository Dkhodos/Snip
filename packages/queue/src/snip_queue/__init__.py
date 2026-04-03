"""snip-queue: shared message queue client package."""

from snip_queue.factory import create_queue_publisher
from snip_queue.messages import ClickEventMessage
from snip_queue.protocol import QueuePublisher
from snip_queue.provider import QueueProvider

__all__ = [
    "ClickEventMessage",
    "QueuePublisher",
    "QueueProvider",
    "create_queue_publisher",
]
