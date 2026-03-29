"""Click event model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from snip_db.models.base import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    link_id: Mapped[UUID] = mapped_column(ForeignKey("links.id"))
    clicked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_agent: Mapped[str | None] = mapped_column(Text, default=None)
    country: Mapped[str | None] = mapped_column(String(2), default=None)
