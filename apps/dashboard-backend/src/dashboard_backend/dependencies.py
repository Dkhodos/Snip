"""FastAPI dependency injection wiring."""

from fastapi import Depends, Request
from snip_db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard_backend.clients.clerk_client import (
    AuthClient,
    ClerkClient,
    ClerkUser,
    DevAuthClient,
)
from dashboard_backend.config import settings
from dashboard_backend.exceptions import AuthenticationError
from dashboard_backend.managers.clicks_manager import ClicksManager
from dashboard_backend.managers.feature_flag_manager import FeatureFlagManager
from dashboard_backend.managers.link_manager import LinkManager
from dashboard_backend.managers.redirect_manager import RedirectManager
from dashboard_backend.managers.seed_manager import SeedManager
from dashboard_backend.stores.click_event_store import ClickEventStore
from dashboard_backend.stores.feature_flag_store import FeatureFlagStore
from dashboard_backend.stores.link_store import LinkStore

# --- Auth client ---


def _is_dev_bypass() -> bool:
    return settings.environment == "development" and (
        not settings.clerk_secret_key or settings.clerk_secret_key == "sk_test_..."
    )


def get_auth_client() -> AuthClient:
    if _is_dev_bypass():
        return DevAuthClient()
    return ClerkClient(settings.clerk_publishable_key)


async def get_current_user(
    request: Request,
    auth_client: AuthClient = Depends(get_auth_client),
) -> ClerkUser:
    if isinstance(auth_client, DevAuthClient):
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


# --- Managers ---


def get_link_manager(
    link_store: LinkStore = Depends(get_link_store),
) -> LinkManager:
    return LinkManager(link_store)


def get_redirect_manager(
    link_store: LinkStore = Depends(get_link_store),
    click_event_store: ClickEventStore = Depends(get_click_event_store),
) -> RedirectManager:
    return RedirectManager(link_store, click_event_store)


def get_clicks_manager(
    link_store: LinkStore = Depends(get_link_store),
    click_event_store: ClickEventStore = Depends(get_click_event_store),
) -> ClicksManager:
    return ClicksManager(link_store, click_event_store)


def get_feature_flag_manager(
    feature_flag_store: FeatureFlagStore = Depends(get_feature_flag_store),
) -> FeatureFlagManager:
    return FeatureFlagManager(feature_flag_store)


def get_seed_manager(
    link_store: LinkStore = Depends(get_link_store),
    click_event_store: ClickEventStore = Depends(get_click_event_store),
) -> SeedManager:
    return SeedManager(link_store, click_event_store)
