"""snip-storage: shared object storage client package."""

from snip_storage.exceptions import (
    BucketNotFoundError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    StorageError,
)
from snip_storage.factory import create_storage_client
from snip_storage.models import StorageObject
from snip_storage.protocol import StorageClient
from snip_storage.provider import StorageProvider

__all__ = [
    "BucketNotFoundError",
    "ObjectAlreadyExistsError",
    "ObjectNotFoundError",
    "StorageClient",
    "StorageError",
    "StorageObject",
    "StorageProvider",
    "create_storage_client",
]
