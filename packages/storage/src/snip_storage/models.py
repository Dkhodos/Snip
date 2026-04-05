"""Storage data models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StorageObject(BaseModel):
    """Immutable object returned from storage read operations."""

    model_config = ConfigDict(frozen=True)

    bucket: str
    key: str
    data: bytes
    size: int
    content_type: str | None = None
    last_modified: datetime | None = None
