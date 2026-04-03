"""Tests for the analytics client factory."""

from unittest.mock import patch

import pytest

from snip_analytics.factory import create_analytics_client
from snip_analytics.provider import AnalyticsProvider
from snip_analytics.providers.dev.client import DevAnalyticsClient
from snip_analytics.providers.gcp.client import BigQueryAnalyticsClient


class TestCreateAnalyticsClient:
    """Tests for create_analytics_client."""

    def test_dev_provider_returns_dev_client(self) -> None:
        client = create_analytics_client(AnalyticsProvider.DEV)
        assert isinstance(client, DevAnalyticsClient)

    @patch("snip_analytics.providers.gcp.client.bigquery.Client")
    def test_default_provider_is_gcp_bigquery(self, _mock_bq: object) -> None:
        client = create_analytics_client(project_id="my-project", dataset="my_dataset")
        assert isinstance(client, BigQueryAnalyticsClient)

    @patch("snip_analytics.providers.gcp.client.bigquery.Client")
    def test_gcp_bigquery_provider_returns_bq_client(self, _mock_bq: object) -> None:
        client = create_analytics_client(
            AnalyticsProvider.GCP_BIGQUERY, project_id="p", dataset="d"
        )
        assert isinstance(client, BigQueryAnalyticsClient)

    def test_gcp_bigquery_without_project_id_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty project_id"):
            create_analytics_client(AnalyticsProvider.GCP_BIGQUERY, dataset="d")

    def test_gcp_bigquery_without_dataset_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty dataset"):
            create_analytics_client(AnalyticsProvider.GCP_BIGQUERY, project_id="p")
