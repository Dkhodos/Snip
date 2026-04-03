"""Analytics client factory."""

from snip_analytics.protocol import AnalyticsClient
from snip_analytics.provider import AnalyticsProvider
from snip_analytics.providers.dev.client import DevAnalyticsClient
from snip_analytics.providers.gcp.client import BigQueryAnalyticsClient


def create_analytics_client(
    provider: AnalyticsProvider = AnalyticsProvider.GCP_BIGQUERY,
    *,
    project_id: str = "",
    dataset: str = "",
    table: str = "click_events",
) -> AnalyticsClient:
    """Create an analytics client for the given provider."""
    if provider == AnalyticsProvider.DEV:
        return DevAnalyticsClient()

    if provider == AnalyticsProvider.GCP_BIGQUERY:
        if not project_id:
            msg = "GCP_BIGQUERY provider requires a non-empty project_id"
            raise ValueError(msg)
        if not dataset:
            msg = "GCP_BIGQUERY provider requires a non-empty dataset"
            raise ValueError(msg)
        return BigQueryAnalyticsClient(project_id=project_id, dataset=dataset, table=table)

    msg = f"Unsupported analytics provider: {provider}"
    raise ValueError(msg)
