"""Tests for the BigQuery analytics client."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from snip_analytics.models import ClickEventRow
from snip_analytics.providers.gcp.client import BigQueryAnalyticsClient


@pytest.fixture
def mock_bq_client() -> MagicMock:
    with patch("snip_analytics.providers.gcp.client.bigquery.Client") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def client(mock_bq_client: MagicMock) -> BigQueryAnalyticsClient:
    return BigQueryAnalyticsClient(project_id="proj", dataset="ds", table="clicks")


@pytest.fixture
def event() -> ClickEventRow:
    return ClickEventRow(
        event_id="evt-1",
        link_id="link-1",
        short_code="abc",
        org_id="org-1",
        clicked_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=UTC),
    )


class TestBigQueryAnalyticsClient:
    async def test_insert_click_event_success(
        self, client: BigQueryAnalyticsClient, mock_bq_client: MagicMock, event: ClickEventRow
    ) -> None:
        mock_bq_client.insert_rows_json.return_value = []
        await client.insert_click_event(event)
        mock_bq_client.insert_rows_json.assert_called_once()
        args = mock_bq_client.insert_rows_json.call_args
        assert args[0][0] == "proj.ds.clicks"

    async def test_insert_click_event_raises_on_errors(
        self, client: BigQueryAnalyticsClient, mock_bq_client: MagicMock, event: ClickEventRow
    ) -> None:
        mock_bq_client.insert_rows_json.return_value = [{"errors": ["some error"]}]
        with pytest.raises(RuntimeError, match="BigQuery insert failed"):
            await client.insert_click_event(event)

    async def test_get_daily_clicks_for_link(
        self, client: BigQueryAnalyticsClient, mock_bq_client: MagicMock
    ) -> None:
        mock_row = MagicMock()
        mock_row.date = "2025-06-01"
        mock_row.count = 5
        mock_job = MagicMock()
        mock_job.result.return_value = [mock_row]
        mock_bq_client.query.return_value = mock_job

        results = await client.get_daily_clicks_for_link("link-1", days=7)
        assert len(results) == 1
        assert results[0].date == "2025-06-01"
        assert results[0].count == 5
        mock_bq_client.query.assert_called_once()

    async def test_get_daily_clicks_for_org(
        self, client: BigQueryAnalyticsClient, mock_bq_client: MagicMock
    ) -> None:
        mock_row = MagicMock()
        mock_row.date = "2025-06-01"
        mock_row.count = 10
        mock_job = MagicMock()
        mock_job.result.return_value = [mock_row]
        mock_bq_client.query.return_value = mock_job

        results = await client.get_daily_clicks_for_org("org-1", days=30)
        assert len(results) == 1
        assert results[0].count == 10
        mock_bq_client.query.assert_called_once()

    def test_full_table_id(self, client: BigQueryAnalyticsClient) -> None:
        assert client._full_table_id == "proj.ds.clicks"
