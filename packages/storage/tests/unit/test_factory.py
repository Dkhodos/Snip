"""Tests for the storage client factory."""

from unittest.mock import patch

import pytest

from snip_storage.factory import create_storage_client
from snip_storage.provider import StorageProvider
from snip_storage.providers.gcs.client import GcsStorageClient
from snip_storage.providers.minio.client import MinioStorageClient

_GCS_CLIENT_PATH = "snip_storage.providers.gcs.client.gcs.Client"


class TestCreateStorageClient:
    def test_minio_provider_returns_minio_client(self) -> None:
        client = create_storage_client(
            StorageProvider.MINIO,
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
        )
        assert isinstance(client, MinioStorageClient)

    def test_minio_without_endpoint_raises(self) -> None:
        with pytest.raises(ValueError, match="endpoint"):
            create_storage_client(StorageProvider.MINIO, access_key="a", secret_key="s")

    def test_minio_without_access_key_raises(self) -> None:
        with pytest.raises(ValueError, match="access_key"):
            create_storage_client(StorageProvider.MINIO, endpoint="localhost:9000", secret_key="s")

    def test_minio_without_secret_key_raises(self) -> None:
        with pytest.raises(ValueError, match="secret_key"):
            create_storage_client(StorageProvider.MINIO, endpoint="localhost:9000", access_key="a")

    def test_gcs_provider_returns_gcs_client(self) -> None:
        with patch(_GCS_CLIENT_PATH):
            client = create_storage_client(StorageProvider.GCS, project_id="my-project")
        assert isinstance(client, GcsStorageClient)

    def test_gcs_without_project_id_raises(self) -> None:
        with pytest.raises(ValueError, match="project_id"):
            create_storage_client(StorageProvider.GCS)

    def test_default_provider_is_gcs(self) -> None:
        with pytest.raises(ValueError, match="project_id"):
            create_storage_client()
