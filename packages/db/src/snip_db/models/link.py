"""Link model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from snip_db.models.base import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    org_id: Mapped[str] = mapped_column(String, index=True)
    short_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    target_url: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(255), default=None)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
