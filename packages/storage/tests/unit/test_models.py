"""Tests for the storage data models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from snip_storage.models import StorageObject


class TestStorageObject:
    def test_create_with_all_fields(self) -> None:
        now = datetime.now(tz=UTC)
        obj = StorageObject(
            bucket="my-bucket",
            key="path/to/file.txt",
            data=b"hello world",
            size=11,
            content_type="text/plain",
            last_modified=now,
        )
        assert obj.bucket == "my-bucket"
        assert obj.key == "path/to/file.txt"
        assert obj.data == b"hello world"
        assert obj.size == 11
        assert obj.content_type == "text/plain"
        assert obj.last_modified == now

    def test_optional_fields_default_to_none(self) -> None:
        obj = StorageObject(bucket="b", key="k", data=b"x", size=1)
        assert obj.content_type is None
        assert obj.last_modified is None

    def test_frozen_immutability(self) -> None:
        obj = StorageObject(bucket="b", key="k", data=b"x", size=1)
        with pytest.raises(ValidationError):
            obj.bucket = "other"  # type: ignore[misc]
