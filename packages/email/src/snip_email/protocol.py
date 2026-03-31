"""Email client protocol and message types."""

from dataclasses import dataclass
from typing import List, Optional, Protocol


@dataclass(frozen=True)
class EmailMessage:
    """Immutable email message DTO."""

    to: List[str]
    subject: str
    html: str


class EmailClient(Protocol):
    """Protocol for email sending clients."""

    async def send(self, message: EmailMessage) -> Optional[str]:
        """Send an email. Returns the provider message ID on success, None on failure."""
        ...
