"""FastAPI dependency injection wiring."""

from fastapi import Depends, Request
from snip_auth import AuthClient, AuthenticationError, AuthProvider, AuthUser, create_auth_client
from snip_db import get_session
from snip_db.stores.click_event_store import ClickEventStore
from snip_db.stores.feature_flag_store import FeatureFlagStore
from snip_db.stores.link_store import LinkStore
from snip_email import EmailClient, EmailProvider, create_email_client
from snip_og_image import OgImageManager
from snip_storage import StorageProvider, create_storage_client
from snip_storage.protocol import StorageClient
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard_backend.config import settings
from dashboard_backend.managers.clicks_manager import ClicksManager
from dashboard_backend.managers.feature_flag_manager import FeatureFlagManager
from dashboard_backend.managers.link_manager import LinkManager
from dashboard_backend.managers.notification_manager import NotificationManager

# --- Auth client ---


def _is_dev_bypass() -> bool:
    return settings.environment == "development" and (
        not settings.clerk_secret_key or settings.clerk_secret_key == "sk_test_..."
    )


def get_auth_client() -> AuthClient:
    if _is_dev_bypass():
        return create_auth_client(AuthProvider.DEV)
    return create_auth_client(AuthProvider.CLERK, publishable_key=settings.clerk_publishable_key)


async def get_current_user(
    request: Request,
    auth_client: AuthClient = Depends(get_auth_client),
) -> AuthUser:
    if _is_dev_bypass():
        return await auth_client.verify_token("")

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise AuthenticationError("Missing authorization token")

    token = auth_header.removeprefix("Bearer ")
    return await auth_client.verify_token(token)


# --- Stores ---


def get_link_store(
    session: AsyncSession = Depends(get_session),
) -> LinkStore:
    return LinkStore(session)


def get_click_event_store(
    session: AsyncSession = Depends(get_session),
) -> ClickEventStore:
    return ClickEventStore(session)


def get_feature_flag_store(
    session: AsyncSession = Depends(get_session),
) -> FeatureFlagStore:
    return FeatureFlagStore(session)


# --- Storage ---

_storage_client: StorageClient | None = None


def get_storage_client() -> StorageClient:
    global _storage_client
    if _storage_client is None:
        _storage_client = create_storage_client(
            StorageProvider(settings.storage_provider),
            endpoint=settings.storage_endpoint,
            access_key=settings.storage_access_key,
            secret_key=settings.storage_secret_key,
            project_id=settings.gcp_project_id,
        )
    return _storage_client


def get_og_image_manager(
    storage_client: StorageClient = Depends(get_storage_client),
) -> OgImageManager:
    return OgImageManager(
        storage_client=storage_client,
        bucket=settings.og_image_bucket,
        redirect_base_url=settings.redirect_base_url,
        og_image_public_url_base=settings.og_image_public_url_base,
    )


# --- Managers ---


def get_link_manager(
    link_store: LinkStore = Depends(get_link_store),
) -> LinkManager:
    return LinkManager(link_store)


def get_clicks_manager(
    link_store: LinkStore = Depends(get_link_store),
    click_event_store: ClickEventStore = Depends(get_click_event_store),
) -> ClicksManager:
    return ClicksManager(link_store, click_event_store)


def get_feature_flag_manager(
    feature_flag_store: FeatureFlagStore = Depends(get_feature_flag_store),
) -> FeatureFlagManager:
    return FeatureFlagManager(feature_flag_store)


# --- Email ---


def get_email_client() -> EmailClient:
    return create_email_client(
        EmailProvider(settings.email_provider),
        api_key=settings.resend_api_key,
        from_email=settings.email_from,
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
    )


async def get_notification_manager(
    email_client: EmailClient = Depends(get_email_client),
    feature_flag_manager: FeatureFlagManager = Depends(get_feature_flag_manager),
) -> NotificationManager:
    flags = await feature_flag_manager.get_all_flags()
    return NotificationManager(
        email_client=email_client,
        feature_flags=flags,
        clerk_secret_key=settings.clerk_secret_key,
        click_threshold=settings.click_threshold,
    )
