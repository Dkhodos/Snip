# Snip

A template for building a link shortener and management platform with analytics. Demonstrates a production-ready Python/React monorepo using uv workspaces, FastAPI microservices, and GCP infrastructure-as-code.

## Architecture

```
                    ┌─────────────────┐
                    │    Frontend     │
                    │  (React SPA)    │
                    └────────┬────────┘
                             │ /api
                    ┌────────▼────────┐        ┌──────────────┐
                    │ Dashboard API   │───────▶│  PostgreSQL   │
                    │   (FastAPI)     │        └──────────────┘
                    └─────────────────┘               ▲
                                                      │
  example.com/r/abc ┌─────────────────┐               │
  ────────────────▶ │ Redirect Service│───────────────┘
                    │   (FastAPI)     │
                    └────────┬────────┘
                             │ publish click event
                    ┌────────▼────────┐
                    │   Pub/Sub       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐        ┌──────────────┐
                    │  Click Worker   │───────▶│   BigQuery    │
                    │   (FastAPI)     │        └──────────────┘
                    └─────────────────┘
```

**Dashboard API** — Link CRUD, user authentication, and click analytics queries.

**Redirect Service** — Resolves `/r/{short_code}` to target URLs, publishes click events to Pub/Sub.

**Click Worker** — Consumes click events from Pub/Sub and writes them to BigQuery.

**Frontend** — React SPA for managing links, viewing analytics, and configuring short URLs.

## Project Structure

```
apps/
  dashboard-backend/    FastAPI — link management API
  dashboard-frontend/   React 19 + TanStack Router — dashboard UI
  redirect-service/     FastAPI — public URL redirect handler
  click-worker/         FastAPI — Pub/Sub → BigQuery click pipeline
  e2e/                  Playwright — end-to-end tests with Clerk auth

packages/
  db/                   SQLAlchemy ORM, Alembic migrations, stores
  auth/                 JWT verification (Clerk / dev bypass)
  email/                Async email (Resend / Mailpit)
  queue/                Message publishing (Pub/Sub / dev)
  analytics/            Click storage + queries (BigQuery / dev)
  og-image/             OG image generation (Pillow + MinIO/GCS)
  storage/              Object storage client (MinIO / GCS)
  logger/               Structured logging with structlog

terraform/              Terragrunt + Terraform — GCP infrastructure
```

See each app/package README for details.

## Tech Stack

| Layer | Tech                                                   |
|-------|--------------------------------------------------------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic        |
| Frontend | React 19, TypeScript, TanStack Router/Query, Tailwind |
| Auth | Clerk                                                  |
| Database | PostgreSQL (asyncpg)                                   |
| Analytics | Google BigQuery                                        |
| Queue | Google Pub/Sub                                         |
| Storage | Google Cloud Storage, MinIO (dev)                      |
| E2E Testing | Playwright                                             |
| Infra | GCP Cloud Run, Terraform, Terragrunt                   |
| Config | [PKL](https://pkl-lang.org/) — typed config generation  |
| Monorepo | uv workspaces                                          |

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Node.js](https://nodejs.org/) 20+ (for frontend)
- [Docker](https://www.docker.com/) (for local services)
- [PKL](https://pkl-lang.org/main/current/pkl-cli/index.html#installation) (typed config language — `brew install pkl`)

### Local Development

Start PostgreSQL and Mailpit:

```bash
docker compose -f dev/docker-compose.yml up -d
```

Install and run the backend:

```bash
make dashboard-backend:install
make db:migrate            # run Alembic migrations
```

Install and run the frontend:

```bash
make dashboard-frontend:install
make dashboard-frontend:dev
```

### Make Targets

All commands follow the pattern `make <project>:<target>`:

```bash
make dashboard-backend:lint
make dashboard-backend:test:unit
make redirect-service:lint
make db:migrate
make dashboard-frontend:dev
```

Run `make help` to list all projects, or `make <project>:help` for project-specific targets.
