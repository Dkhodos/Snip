"""Storage provider enum."""

from enum import StrEnum


class StorageProvider(StrEnum):
    """Supported storage providers."""

    MINIO = "minio"
    GCS = "gcs"
