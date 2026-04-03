"""Queue client protocol and message types."""

from typing import Protocol


class QueuePublisher(Protocol):
    """Protocol for publishing messages to a queue."""

    async def publish(
        self, topic: str, data: bytes, *, attributes: dict[str, str] | None = None
    ) -> str:
        """Publish a message. Returns the message ID."""
        ...
