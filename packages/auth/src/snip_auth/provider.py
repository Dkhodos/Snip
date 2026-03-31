"""Auth provider enum."""

from enum import StrEnum


class AuthProvider(StrEnum):
    """Supported auth providers."""

    CLERK = "clerk"
    DEV = "dev"
