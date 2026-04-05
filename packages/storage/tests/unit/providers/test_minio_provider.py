"""Tests for the MinIO storage provider."""

import logging
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from minio.error import S3Error

from snip_storage.exceptions import (
    BucketNotFoundError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)
from snip_storage.models import StorageObject
from snip_storage.providers.minio.client import MinioStorageClient

_CLIENT_PATH = "snip_storage.providers.minio.client.Minio"


@pytest.fixture
def mock_minio() -> MagicMock:
    with patch(_CLIENT_PATH) as mock_cls:
        yield mock_cls.return_value


@pytest.fixture
def client(mock_minio: MagicMock) -> MinioStorageClient:
    return MinioStorageClient(endpoint="localhost:9000", access_key="ak", secret_key="sk")


def _s3_error(code: str) -> S3Error:
    return S3Error(
        code=code,
        message=f"mock {code}",
        resource="/test",
        request_id="req-1",
        host_id="host-1",
        response=None,  # type: ignore[arg-type]
    )


class TestMinioRead:
    async def test_read_returns_storage_object(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        response = MagicMock()
        response.read.return_value = b"hello"
        mock_minio.get_object.return_value = response

        stat = MagicMock()
        stat.size = 5
        stat.content_type = "text/plain"
        stat.last_modified = datetime(2025, 1, 1, tzinfo=UTC)
        mock_minio.stat_object.return_value = stat

        result = await client.read("bucket", "key")

        assert isinstance(result, StorageObject)
        assert result.data == b"hello"
        assert result.size == 5
        assert result.content_type == "text/plain"
        assert result.last_modified == datetime(2025, 1, 1, tzinfo=UTC)

    async def test_read_not_found_returns_none(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.get_object.side_effect = _s3_error("NoSuchKey")
        result = await client.read("bucket", "missing-key")
        assert result is None

    async def test_read_bucket_not_found_raises(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.get_object.side_effect = _s3_error("NoSuchBucket")
        with pytest.raises(BucketNotFoundError):
            await client.read("bad-bucket", "key")


class TestMinioWrite:
    async def test_write_creates_object(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.stat_object.side_effect = _s3_error("NoSuchKey")

        await client.write("bucket", "key", b"data")

        mock_minio.put_object.assert_called_once()

    async def test_write_existing_key_raises(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.stat_object.return_value = MagicMock()

        with pytest.raises(ObjectAlreadyExistsError):
            await client.write("bucket", "existing-key", b"data")

    async def test_write_bucket_not_found_raises(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.stat_object.side_effect = _s3_error("NoSuchBucket")

        with pytest.raises(BucketNotFoundError):
            await client.write("bad-bucket", "key", b"data")

    async def test_write_logs_on_success(
        self,
        client: MinioStorageClient,
        mock_minio: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mock_minio.stat_object.side_effect = _s3_error("NoSuchKey")

        with caplog.at_level(logging.INFO):
            await client.write("bucket", "key", b"data")

        assert "object_written" in caplog.text
        assert "minio" in caplog.text


class TestMinioUpsert:
    async def test_upsert_creates_object(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        await client.upsert("bucket", "key", b"data")
        mock_minio.put_object.assert_called_once()

    async def test_upsert_overwrites_existing(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        await client.upsert("bucket", "key", b"new-data")
        mock_minio.put_object.assert_called_once()
        mock_minio.stat_object.assert_not_called()

    async def test_upsert_logs_on_success(
        self,
        client: MinioStorageClient,
        mock_minio: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        with caplog.at_level(logging.INFO):
            await client.upsert("bucket", "key", b"data")

        assert "object_upserted" in caplog.text


class TestMinioDelete:
    async def test_delete_removes_object(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.stat_object.return_value = MagicMock()

        await client.delete("bucket", "key")

        mock_minio.remove_object.assert_called_once_with("bucket", "key")

    async def test_delete_not_found_raises(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.stat_object.side_effect = _s3_error("NoSuchKey")

        with pytest.raises(ObjectNotFoundError):
            await client.delete("bucket", "missing-key")

    async def test_delete_bucket_not_found_raises(
        self, client: MinioStorageClient, mock_minio: MagicMock
    ) -> None:
        mock_minio.stat_object.side_effect = _s3_error("NoSuchBucket")

        with pytest.raises(BucketNotFoundError):
            await client.delete("bad-bucket", "key")

    async def test_delete_logs_on_success(
        self,
        client: MinioStorageClient,
        mock_minio: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mock_minio.stat_object.return_value = MagicMock()

        with caplog.at_level(logging.INFO):
            await client.delete("bucket", "key")

        assert "object_deleted" in caplog.text
        assert "minio" in caplog.text
