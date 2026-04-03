"""Analytics provider enum."""

from enum import StrEnum


class AnalyticsProvider(StrEnum):
    """Supported analytics providers."""

    GCP_BIGQUERY = "gcp_bigquery"
    DEV = "dev"
