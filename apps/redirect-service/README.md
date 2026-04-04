# Redirect Service

Public-facing FastAPI service that handles short link redirects and publishes click events.

## Routes

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/r/{short_code}` | Resolve short code and redirect to target URL |
| `GET` | `/health` | Health check |

On each redirect, publishes a `ClickEventMessage` to the configured queue for async analytics processing.

## Dependencies

Uses shared packages: `snip-db`, `snip-queue`, `snip-logger`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `ENVIRONMENT` | `development` | `development` / `staging` / `production` |
| `QUEUE_PROVIDER` | `dev` | `dev` / `gcp_pubsub` |
| `GCP_PROJECT_ID` | — | GCP project (required for Pub/Sub) |
| `CLICK_TOPIC` | `click-events` | Pub/Sub topic name |

## Running

```bash
make redirect-service:install
make redirect-service:lint
make redirect-service:test:unit
```

Port: **8080**
