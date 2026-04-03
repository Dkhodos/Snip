"""Google BigQuery analytics client."""

import logging
from datetime import UTC, datetime, timedelta

from google.cloud import bigquery

from snip_analytics.models import ClickEventRow, DailyClickCount
from snip_analytics.protocol import AnalyticsClient

_log = logging.getLogger(__name__)


class BigQueryAnalyticsClient:
    """Analytics client backed by Google BigQuery."""

    def __init__(self, project_id: str, dataset: str, table: str = "click_events") -> None:
        self._project_id = project_id
        self._dataset = dataset
        self._table = table
        self._client = bigquery.Client(project=project_id)
        self._full_table_id = f"{project_id}.{dataset}.{table}"

    async def insert_click_event(self, event: ClickEventRow) -> None:
        """Insert a click event via streaming insert."""
        errors = self._client.insert_rows_json(self._full_table_id, [event.to_bq_row()])
        if errors:
            _log.error("bigquery_insert_error table=%s errors=%s", self._full_table_id, errors)
            msg = f"BigQuery insert failed: {errors}"
            raise RuntimeError(msg)
        _log.info("click_event_inserted table=%s event_id=%s", self._full_table_id, event.event_id)

    async def get_daily_clicks_for_link(
        self, link_id: str, *, days: int = 7
    ) -> list[DailyClickCount]:
        """Query daily click counts for a link."""
        since = datetime.now(tz=UTC) - timedelta(days=days)
        query = f"""
            SELECT DATE(clicked_at) AS date, COUNT(*) AS count
            FROM `{self._full_table_id}`
            WHERE link_id = @link_id AND clicked_at >= @since
            GROUP BY date
            ORDER BY date
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("link_id", "STRING", link_id),
                bigquery.ScalarQueryParameter("since", "TIMESTAMP", since),
            ]
        )
        results = self._client.query(query, job_config=job_config).result()
        return [DailyClickCount(date=str(row.date), count=row.count) for row in results]

    async def get_daily_clicks_for_org(
        self, org_id: str, *, days: int = 30
    ) -> list[DailyClickCount]:
        """Query daily click counts for an organization."""
        since = datetime.now(tz=UTC) - timedelta(days=days)
        query = f"""
            SELECT DATE(clicked_at) AS date, COUNT(*) AS count
            FROM `{self._full_table_id}`
            WHERE org_id = @org_id AND clicked_at >= @since
            GROUP BY date
            ORDER BY date
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("org_id", "STRING", org_id),
                bigquery.ScalarQueryParameter("since", "TIMESTAMP", since),
            ]
        )
        results = self._client.query(query, job_config=job_config).result()
        return [DailyClickCount(date=str(row.date), count=row.count) for row in results]


def _assert_implements_protocol() -> None:
    _: AnalyticsClient = BigQueryAnalyticsClient(project_id="p", dataset="d")  # noqa: F841
