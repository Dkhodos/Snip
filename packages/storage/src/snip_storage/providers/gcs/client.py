"""Google Cloud Storage provider."""

import asyncio
import logging

from google.cloud import storage as gcs
from google.cloud.exceptions import NotFound

from snip_storage.exceptions import (
    BucketNotFoundError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)
from snip_storage.models import StorageObject
from snip_storage.protocol import StorageClient

_log = logging.getLogger(__name__)


class GcsStorageClient:
    """Storage client backed by Google Cloud Storage."""

    def __init__(self, project_id: str) -> None:
        self._client = gcs.Client(project=project_id)

    async def read(self, bucket: str, key: str) -> StorageObject | None:
        try:
            blob = self._client.bucket(bucket).blob(key)
            data = await asyncio.to_thread(blob.download_as_bytes)
            return StorageObject(
                bucket=bucket,
                key=key,
                data=data,
                size=blob.size or len(data),
                content_type=blob.content_type,
                last_modified=blob.updated,
            )
        except NotFound:
            return None

    async def write(
        self, bucket: str, key: str, data: bytes, *, content_type: str | None = None
    ) -> None:
        gcs_bucket = self._client.bucket(bucket)
        try:
            await asyncio.to_thread(gcs_bucket.reload)
        except NotFound as exc:
            raise BucketNotFoundError(bucket) from exc

        blob = gcs_bucket.blob(key)
        exists = await asyncio.to_thread(blob.exists)
        if exists:
            raise ObjectAlreadyExistsError(bucket, key)

        await asyncio.to_thread(
            blob.upload_from_string, data, content_type=content_type or "application/octet-stream"
        )
        _log.info("object_written provider=gcs bucket=%s key=%s size=%d", bucket, key, len(data))

    async def upsert(
        self, bucket: str, key: str, data: bytes, *, content_type: str | None = None
    ) -> None:
        gcs_bucket = self._client.bucket(bucket)
        try:
            await asyncio.to_thread(gcs_bucket.reload)
        except NotFound as exc:
            raise BucketNotFoundError(bucket) from exc

        blob = gcs_bucket.blob(key)
        await asyncio.to_thread(
            blob.upload_from_string, data, content_type=content_type or "application/octet-stream"
        )
        _log.info("object_upserted provider=gcs bucket=%s key=%s size=%d", bucket, key, len(data))

    async def delete(self, bucket: str, key: str) -> None:
        gcs_bucket = self._client.bucket(bucket)
        try:
            await asyncio.to_thread(gcs_bucket.reload)
        except NotFound as exc:
            raise BucketNotFoundError(bucket) from exc

        blob = gcs_bucket.blob(key)
        exists = await asyncio.to_thread(blob.exists)
        if not exists:
            raise ObjectNotFoundError(bucket, key)

        await asyncio.to_thread(blob.delete)
        _log.info("object_deleted provider=gcs bucket=%s key=%s", bucket, key)


def _assert_implements_protocol() -> None:
    """Compile-time check that GcsStorageClient satisfies StorageClient."""
    _: StorageClient = GcsStorageClient(project_id="test")  # noqa: F841
