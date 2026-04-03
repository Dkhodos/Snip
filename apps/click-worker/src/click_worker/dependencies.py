"""FastAPI dependency injection wiring."""

from snip_analytics import AnalyticsClient, AnalyticsProvider, create_analytics_client

from click_worker.config import settings

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
