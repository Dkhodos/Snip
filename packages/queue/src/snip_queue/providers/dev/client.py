"""Dev queue publisher that logs instead of publishing."""

import logging
import uuid

from snip_queue.protocol import QueuePublisher

_log = logging.getLogger(__name__)


class DevQueuePublisher:
    """Dev bypass queue publisher that logs messages."""

    def __init__(self) -> None:
        self.published: list[tuple[str, bytes, dict[str, str] | None]] = []

    async def publish(
        self, topic: str, data: bytes, *, attributes: dict[str, str] | None = None
    ) -> str:
        message_id = f"dev_{uuid.uuid4().hex[:12]}"
        self.published.append((topic, data, attributes))
        _log.info(
            "message_published topic=%s message_id=%s data_size=%d",
            topic,
            message_id,
            len(data),
        )
        return message_id


def _assert_implements_protocol() -> None:
    _: QueuePublisher = DevQueuePublisher()  # noqa: F841
