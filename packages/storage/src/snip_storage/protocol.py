"""Storage client protocol."""

from typing import Protocol

from snip_storage.models import StorageObject


class StorageClient(Protocol):
    """Protocol for object storage clients."""

    async def read(self, bucket: str, key: str) -> StorageObject | None:
        """Read an object. Returns None if not found."""
        ...

    async def write(
        self, bucket: str, key: str, data: bytes, *, content_type: str | None = None
    ) -> None:
        """Write an object. Raises ObjectAlreadyExistsError if key exists."""
        ...

    async def upsert(
        self, bucket: str, key: str, data: bytes, *, content_type: str | None = None
    ) -> None:
        """Write an object, overwriting if it already exists."""
        ...

    async def delete(self, bucket: str, key: str) -> None:
        """Delete an object. Raises ObjectNotFoundError if not found."""
        ...
