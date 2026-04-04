# snip-analytics

Click event storage and aggregation with pluggable providers.

## Protocol

```python
class AnalyticsClient(Protocol):
    async def insert_click_event(self, event: ClickEventRow) -> None: ...
    async def get_daily_clicks_for_link(self, link_id: str, days: int) -> list[DailyClickCount]: ...
    async def get_daily_clicks_for_org(self, org_id: str, days: int) -> list[DailyClickCount]: ...
```

## Providers

| Provider | Usage |
|----------|-------|
| `GCP_BIGQUERY` | Production — reads/writes via Google BigQuery |
| `DEV` | Local dev — in-memory store (data lost on restart) |

## Usage

```python
from snip_analytics import create_analytics_client, AnalyticsProvider

client = create_analytics_client(AnalyticsProvider.GCP_BIGQUERY, project_id="my-project", dataset="analytics", table="click_events")
await client.insert_click_event(event)
daily = await client.get_daily_clicks_for_link("link_123", days=30)
```
