"""FastAPI dependency injection wiring."""

from fastapi import Depends
from snip_db import get_session
from snip_db.stores.link_store import LinkStore
from snip_queue import QueueProvider, QueuePublisher, create_queue_publisher
from sqlalchemy.ext.asyncio import AsyncSession

from redirect_service.config import settings
from redirect_service.managers.redirect_manager import RedirectManager

# --- Queue publisher (singleton) ---

_publisher: QueuePublisher | None = None


def get_queue_publisher() -> QueuePublisher:
    global _publisher
    if _publisher is None:
        _publisher = create_queue_publisher(
            QueueProvider(settings.queue_provider),
            project_id=settings.gcp_project_id,
        )
    return _publisher


# --- Stores ---


def get_link_store(session: AsyncSession = Depends(get_session)) -> LinkStore:
    return LinkStore(session)


# --- Managers ---


def get_redirect_manager(
    link_store: LinkStore = Depends(get_link_store),
    publisher: QueuePublisher = Depends(get_queue_publisher),
) -> RedirectManager:
    return RedirectManager(
        link_store=link_store,
        publisher=publisher,
        click_topic=settings.click_topic,
    )
