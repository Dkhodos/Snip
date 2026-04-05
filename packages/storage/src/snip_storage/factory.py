"""Storage client factory."""

from snip_storage.protocol import StorageClient
from snip_storage.provider import StorageProvider
from snip_storage.providers.gcs.client import GcsStorageClient
from snip_storage.providers.minio.client import MinioStorageClient


def create_storage_client(
    provider: StorageProvider = StorageProvider.GCS,
    *,
    endpoint: str = "",
    access_key: str = "",
    secret_key: str = "",
    secure: bool = False,
    project_id: str = "",
) -> StorageClient:
    """Create a storage client for the given provider.

    For MINIO, ``endpoint``, ``access_key``, and ``secret_key`` are required.
    For GCS, ``project_id`` is required.
    """
    if provider == StorageProvider.MINIO:
        if not endpoint:
            msg = "MINIO provider requires a non-empty endpoint"
            raise ValueError(msg)
        if not access_key:
            msg = "MINIO provider requires a non-empty access_key"
            raise ValueError(msg)
        if not secret_key:
            msg = "MINIO provider requires a non-empty secret_key"
            raise ValueError(msg)
        return MinioStorageClient(
            endpoint=endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )

    if provider == StorageProvider.GCS:
        if not project_id:
            msg = "GCS provider requires a non-empty project_id"
            raise ValueError(msg)
        return GcsStorageClient(project_id=project_id)

    msg = f"Unsupported storage provider: {provider}"
    raise ValueError(msg)
