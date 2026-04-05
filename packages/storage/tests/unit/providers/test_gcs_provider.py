"""Tests for the GCS storage provider."""

import logging
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from google.cloud.exceptions import NotFound

from snip_storage.exceptions import (
    BucketNotFoundError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)
from snip_storage.models import StorageObject
from snip_storage.providers.gcs.client import GcsStorageClient

_CLIENT_PATH = "snip_storage.providers.gcs.client.gcs.Client"


@pytest.fixture
def mock_gcs() -> MagicMock:
    with patch(_CLIENT_PATH) as mock_cls:
        yield mock_cls.return_value


@pytest.fixture
def client(mock_gcs: MagicMock) -> GcsStorageClient:
    return GcsStorageClient(project_id="test-project")


class TestGcsRead:
    async def test_read_returns_storage_object(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        blob = MagicMock()
        blob.download_as_bytes.return_value = b"hello"
        blob.size = 5
        blob.content_type = "text/plain"
        blob.updated = datetime(2025, 1, 1, tzinfo=UTC)
        mock_gcs.bucket.return_value.blob.return_value = blob

        result = await client.read("bucket", "key")

        assert isinstance(result, StorageObject)
        assert result.data == b"hello"
        assert result.size == 5
        assert result.content_type == "text/plain"
        assert result.last_modified == datetime(2025, 1, 1, tzinfo=UTC)

    async def test_read_not_found_returns_none(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        blob = MagicMock()
        blob.download_as_bytes.side_effect = NotFound("not found")
        mock_gcs.bucket.return_value.blob.return_value = blob

        result = await client.read("bucket", "missing-key")
        assert result is None


class TestGcsWrite:
    async def test_write_creates_object(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        blob.exists.return_value = False
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        await client.write("bucket", "key", b"data")

        blob.upload_from_string.assert_called_once()

    async def test_write_existing_key_raises(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        blob.exists.return_value = True
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        with pytest.raises(ObjectAlreadyExistsError):
            await client.write("bucket", "existing-key", b"data")

    async def test_write_bucket_not_found_raises(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        bucket_mock.reload.side_effect = NotFound("bucket not found")
        mock_gcs.bucket.return_value = bucket_mock

        with pytest.raises(BucketNotFoundError):
            await client.write("bad-bucket", "key", b"data")

    async def test_write_logs_on_success(
        self,
        client: GcsStorageClient,
        mock_gcs: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        blob.exists.return_value = False
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        with caplog.at_level(logging.INFO):
            await client.write("bucket", "key", b"data")

        assert "object_written" in caplog.text
        assert "gcs" in caplog.text


class TestGcsUpsert:
    async def test_upsert_creates_object(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        await client.upsert("bucket", "key", b"data")

        blob.upload_from_string.assert_called_once()

    async def test_upsert_bucket_not_found_raises(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        bucket_mock.reload.side_effect = NotFound("bucket not found")
        mock_gcs.bucket.return_value = bucket_mock

        with pytest.raises(BucketNotFoundError):
            await client.upsert("bad-bucket", "key", b"data")

    async def test_upsert_logs_on_success(
        self,
        client: GcsStorageClient,
        mock_gcs: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        with caplog.at_level(logging.INFO):
            await client.upsert("bucket", "key", b"data")

        assert "object_upserted" in caplog.text


class TestGcsDelete:
    async def test_delete_removes_object(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        blob.exists.return_value = True
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        await client.delete("bucket", "key")

        blob.delete.assert_called_once()

    async def test_delete_not_found_raises(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        blob.exists.return_value = False
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        with pytest.raises(ObjectNotFoundError):
            await client.delete("bucket", "missing-key")

    async def test_delete_bucket_not_found_raises(
        self, client: GcsStorageClient, mock_gcs: MagicMock
    ) -> None:
        bucket_mock = MagicMock()
        bucket_mock.reload.side_effect = NotFound("bucket not found")
        mock_gcs.bucket.return_value = bucket_mock

        with pytest.raises(BucketNotFoundError):
            await client.delete("bad-bucket", "key")

    async def test_delete_logs_on_success(
        self,
        client: GcsStorageClient,
        mock_gcs: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        bucket_mock = MagicMock()
        blob = MagicMock()
        blob.exists.return_value = True
        bucket_mock.blob.return_value = blob
        mock_gcs.bucket.return_value = bucket_mock

        with caplog.at_level(logging.INFO):
            await client.delete("bucket", "key")

        assert "object_deleted" in caplog.text
        assert "gcs" in caplog.text
