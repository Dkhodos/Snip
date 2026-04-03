"""Queue provider enum."""

from enum import StrEnum


class QueueProvider(StrEnum):
    """Supported queue providers."""

    GCP_PUBSUB = "gcp_pubsub"
    DEV = "dev"
