"""Email provider enum."""

from enum import StrEnum


class EmailProvider(StrEnum):
    """Supported email providers."""

    RESEND = "resend"
    MAILPIT = "mailpit"
