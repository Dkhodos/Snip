"""Storage exception hierarchy."""


class StorageError(Exception):
    """Base exception for all storage operations."""


class ObjectNotFoundError(StorageError):
    """Raised when a requested object does not exist."""

    def __init__(self, bucket: str, key: str) -> None:
        self.bucket = bucket
        self.key = key
        super().__init__(f"Object not found: {bucket}/{key}")


class ObjectAlreadyExistsError(StorageError):
    """Raised when writing to a key that already exists."""

    def __init__(self, bucket: str, key: str) -> None:
        self.bucket = bucket
        self.key = key
        super().__init__(f"Object already exists: {bucket}/{key}")


class BucketNotFoundError(StorageError):
    """Raised when the target bucket does not exist."""

    def __init__(self, bucket: str) -> None:
        self.bucket = bucket
        super().__init__(f"Bucket not found: {bucket}")
