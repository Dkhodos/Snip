"""FastAPI dependency injection wiring."""

import google.auth.transport.requests
import google.oauth2.id_token
from fastapi import HTTPException, Request
from snip_analytics import AnalyticsClient, AnalyticsProvider, create_analytics_client
from snip_logger import get_logger

from click_worker.config import settings

_log = get_logger("click-worker", log_prefix="Auth")

# --- Analytics client (singleton) ---

_client: AnalyticsClient | None = None


def get_analytics_client() -> AnalyticsClient:
    global _client
    if _client is None:
        _client = create_analytics_client(
            AnalyticsProvider(settings.analytics_provider),
            project_id=settings.gcp_project_id,
            dataset=settings.bq_dataset,
            table=settings.bq_table,
        )
    return _client


# --- Pub/Sub push token verification ---

_google_request = google.auth.transport.requests.Request()


def verify_pubsub_token(request: Request) -> None:
    """Verify GCP OIDC token attached by Pub/Sub push subscriptions.

    Skipped when ``enable_pubsub_auth=False`` (local dev / tests).
    """
    if not settings.enable_pubsub_auth:
        return

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        _log.warning("pubsub_auth_missing_token")
        raise HTTPException(status_code=401, detail="Missing Pub/Sub auth token")

    token = auth_header.removeprefix("Bearer ")
    try:
        google.oauth2.id_token.verify_oauth2_token(
            token,
            _google_request,
            audience=settings.pubsub_audience,
        )
    except Exception as e:
        _log.warning("pubsub_auth_invalid_token", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid Pub/Sub token") from e
