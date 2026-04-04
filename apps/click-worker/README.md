# Click Worker

Background worker that consumes click events from Pub/Sub and writes them to BigQuery.

## How It Works

1. Receives push messages from Google Pub/Sub via HTTP endpoint
2. Deserializes `ClickEventMessage` from the message payload
3. Writes the event to BigQuery via the analytics client

## Dependencies

Uses shared packages: `snip-queue`, `snip-analytics`, `snip-logger`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `development` / `staging` / `production` |
| `ANALYTICS_PROVIDER` | `dev` | `dev` / `gcp_bigquery` |
| `GCP_PROJECT_ID` | — | GCP project (required for BigQuery) |
| `BQ_DATASET` | — | BigQuery dataset name |
| `BQ_TABLE` | `click_events` | BigQuery table name |

## Running

```bash
make click-worker:install
make click-worker:lint
make click-worker:test:unit
```

Port: **8080**
