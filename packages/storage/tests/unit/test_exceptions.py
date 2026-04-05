"""Tests for the storage exception hierarchy."""

from snip_storage.exceptions import (
    BucketNotFoundError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    StorageError,
)


class TestStorageErrorHierarchy:
    def test_all_exceptions_inherit_from_storage_error(self) -> None:
        assert issubclass(ObjectNotFoundError, StorageError)
        assert issubclass(ObjectAlreadyExistsError, StorageError)
        assert issubclass(BucketNotFoundError, StorageError)


class TestObjectNotFoundError:
    def test_message_format(self) -> None:
        exc = ObjectNotFoundError(bucket="my-bucket", key="path/to/file.txt")
        assert str(exc) == "Object not found: my-bucket/path/to/file.txt"

    def test_attributes(self) -> None:
        exc = ObjectNotFoundError(bucket="b", key="k")
        assert exc.bucket == "b"
        assert exc.key == "k"


class TestObjectAlreadyExistsError:
    def test_message_format(self) -> None:
        exc = ObjectAlreadyExistsError(bucket="my-bucket", key="path/to/file.txt")
        assert str(exc) == "Object already exists: my-bucket/path/to/file.txt"

    def test_attributes(self) -> None:
        exc = ObjectAlreadyExistsError(bucket="b", key="k")
        assert exc.bucket == "b"
        assert exc.key == "k"


class TestBucketNotFoundError:
    def test_message_format(self) -> None:
        exc = BucketNotFoundError(bucket="my-bucket")
        assert str(exc) == "Bucket not found: my-bucket"

    def test_attributes(self) -> None:
        exc = BucketNotFoundError(bucket="b")
        assert exc.bucket == "b"
