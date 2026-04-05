"""MinIO storage provider for local development."""

import asyncio
import io
import logging

from minio import Minio
from minio.error import S3Error

from snip_storage.exceptions import (
    BucketNotFoundError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)
from snip_storage.models import StorageObject
from snip_storage.protocol import StorageClient

_log = logging.getLogger(__name__)


class MinioStorageClient:
    """Storage client backed by MinIO (S3-compatible)."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        *,
        secure: bool = False,
    ) -> None:
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    async def read(self, bucket: str, key: str) -> StorageObject | None:
        try:
            response = await asyncio.to_thread(self._client.get_object, bucket, key)
            try:
                data = response.read()
            finally:
                response.close()
                response.release_conn()

            stat = await asyncio.to_thread(self._client.stat_object, bucket, key)
            return StorageObject(
                bucket=bucket,
                key=key,
                data=data,
                size=stat.size or len(data),
                content_type=stat.content_type,
                last_modified=stat.last_modified,
            )
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                return None
            if exc.code == "NoSuchBucket":
                raise BucketNotFoundError(bucket) from exc
            raise

    async def write(
        self, bucket: str, key: str, data: bytes, *, content_type: str | None = None
    ) -> None:
        try:
            await asyncio.to_thread(self._client.stat_object, bucket, key)
            raise ObjectAlreadyExistsError(bucket, key)
        except S3Error as exc:
            if exc.code == "NoSuchBucket":
                raise BucketNotFoundError(bucket) from exc
            if exc.code != "NoSuchKey":
                raise

        await self._put(bucket, key, data, content_type)
        _log.info("object_written provider=minio bucket=%s key=%s size=%d", bucket, key, len(data))

    async def upsert(
        self, bucket: str, key: str, data: bytes, *, content_type: str | None = None
    ) -> None:
        await self._put(bucket, key, data, content_type)
        _log.info("object_upserted provider=minio bucket=%s key=%s size=%d", bucket, key, len(data))

    async def delete(self, bucket: str, key: str) -> None:
        try:
            await asyncio.to_thread(self._client.stat_object, bucket, key)
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                raise ObjectNotFoundError(bucket, key) from exc
            if exc.code == "NoSuchBucket":
                raise BucketNotFoundError(bucket) from exc
            raise

        await asyncio.to_thread(self._client.remove_object, bucket, key)
        _log.info("object_deleted provider=minio bucket=%s key=%s", bucket, key)

    async def _put(self, bucket: str, key: str, data: bytes, content_type: str | None) -> None:
        try:
            await asyncio.to_thread(
                self._client.put_object,
                bucket,
                key,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type or "application/octet-stream",
            )
        except S3Error as exc:
            if exc.code == "NoSuchBucket":
                raise BucketNotFoundError(bucket) from exc
            raise


def _assert_implements_protocol() -> None:
    """Compile-time check that MinioStorageClient satisfies StorageClient."""
    _: StorageClient = MinioStorageClient(  # noqa: F841
        endpoint="", access_key="", secret_key=""
    )
