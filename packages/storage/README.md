# snip-storage

Shared object storage client package with pluggable providers.

## Providers

| Provider | SDK | Use Case |
|----------|-----|----------|
| `MINIO` | `minio` | Local development (S3-compatible) |
| `GCS` | `google-cloud-storage` | Production (Google Cloud Storage) |

## Protocol

```python
class StorageClient(Protocol):
    async def read(self, bucket: str, key: str) -> StorageObject | None: ...
    async def write(self, bucket: str, key: str, data: bytes, *, content_type: str | None = None) -> None: ...
    async def upsert(self, bucket: str, key: str, data: bytes, *, content_type: str | None = None) -> None: ...
```

- **read** — Returns a `StorageObject` or `None` if not found.
- **write** — Create-only. Raises `ObjectAlreadyExistsError` if the key exists.
- **upsert** — Create-or-replace. Overwrites silently.

## Usage

```python
from snip_storage import StorageProvider, create_storage_client

# Local development (MinIO)
client = create_storage_client(
    StorageProvider.MINIO,
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
)

# Production (GCS)
client = create_storage_client(
    StorageProvider.GCS,
    project_id="my-gcp-project",
)

# Read
obj = await client.read("my-bucket", "path/to/file.txt")
if obj:
    print(obj.data, obj.size, obj.content_type)

# Write (fails if exists)
await client.write("my-bucket", "path/to/file.txt", b"hello")

# Upsert (overwrites if exists)
await client.upsert("my-bucket", "path/to/file.txt", b"hello")
```

## Exceptions

All exceptions inherit from `StorageError`:

- `ObjectNotFoundError` — object does not exist
- `ObjectAlreadyExistsError` — write conflict (key already present)
- `BucketNotFoundError` — target bucket does not exist
