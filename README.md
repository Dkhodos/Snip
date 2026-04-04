# Snip

Link shortener and management platform with analytics.

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
  short.link/r/abc  ┌─────────────────┐               │
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

**Dashboard API** manages links (CRUD), authenticates users via Clerk, and queries click analytics.

**Redirect Service** handles public short link requests (`/r/{short_code}`), resolves the target URL, and publishes a click event to Pub/Sub.

**Click Worker** consumes click events from Pub/Sub and writes them to BigQuery for time-series analytics.

**Frontend** is a React SPA for managing links, viewing analytics, and configuring short URLs.

## Project Structure

```
apps/
  dashboard-backend/    FastAPI — link management API
  dashboard-frontend/   React 19 + TanStack Router — dashboard UI
  redirect-service/     FastAPI — public URL redirect handler
  click-worker/         FastAPI — Pub/Sub → BigQuery click pipeline

packages/
  db/                   SQLAlchemy ORM, Alembic migrations, stores
  auth/                 JWT verification (Clerk / dev bypass)
  email/                Async email (Resend / Mailpit)
  queue/                Message publishing (Pub/Sub / dev)
  analytics/            Click storage + queries (BigQuery / dev)
  logger/               Structured logging with structlog
```

See each app/package README for details.

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic |
| Frontend | React 19, TypeScript, TanStack Router/Query, Tailwind |
| Auth | Clerk |
| Database | PostgreSQL (asyncpg) |
| Analytics | Google BigQuery |
| Queue | Google Pub/Sub |
| Infra | GCP Cloud Run, Terraform, Terragrunt |
| Monorepo | uv workspaces |

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Node.js](https://nodejs.org/) 20+ (for frontend)
- [Docker](https://www.docker.com/) (for local services)

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
