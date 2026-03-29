# PLAN.md — B2B URL Shortener (Stack Validation Project)

> **Purpose:** A focused test project to validate the full startup stack before applying it to the real product.
> Build this end-to-end, in order. Each phase is independently deployable.

---

## Stack Being Validated

| Layer | Tool | Status |
|---|---|---|
| Compute | Cloud Run (Cloud Run Jobs for async) | Deferred |
| Frontend | Vite + React + TanStack Router → Cloudflare Pages | **Done (local)** |
| UI | shadcn/ui (dark mode) | **Done** |
| State | React Query (TanStack Query) | **Done** |
| Frontend Linting | Biome | **Done** |
| Frontend Testing | Vitest | Configured, tests TBD |
| Backend | Python / FastAPI | **Done** |
| Backend Linting | Ruff | **Done** |
| Backend Testing | pytest | Configured, tests TBD |
| Auth | Clerk (B2B orgs) | **Done** (dev bypass) |
| Operational DB | Cloud SQL (Postgres) | **Done (local)** |
| ORM / Migrations | SQLAlchemy + Alembic | **Done** |
| Queue | Pub/Sub | Deferred |
| Analytics DB | BigQuery | Deferred |
| CI/CD | GitHub Actions + OIDC | Deferred |
| Secrets | Infisical → GCP Secret Manager | Deferred |
| IaC | Terraform (state in GCS) | Deferred |
| Back Office | Appsmith (self-hosted on Cloud Run) | Deferred |
| Feature Flags | Cloud SQL table (managed via Appsmith) | **Done** |
| Error Tracking | Sentry | Deferred |
| Email | Resend | Deferred |
| CDN / DNS | Cloudflare Pages + Cloudflare DNS | Deferred |

---

## Repo Structure

```
/
├── apps/
│   ├── dashboard-backend/            # FastAPI backend → Cloud Run
│   │   ├── src/
│   │   │   └── dashboard_backend/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── config.py
│   │   │       ├── clerk.py          # JWT validation middleware
│   │   │       └── routers/
│   │   │           ├── __init__.py
│   │   │           ├── links.py
│   │   │           ├── redirect.py
│   │   │           ├── clicks.py
│   │   │           ├── flags.py
│   │   │           ├── stats.py
│   │   │           └── seed.py       # Dev-only, conditionally mounted
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml            # depends on "snip-db[pg]"
│   │
│   └── dashboard-frontend/           # Vite SPA → Cloudflare Pages
│       ├── src/
│       │   ├── main.tsx
│       │   ├── globals.css           # Snip brand colors + fonts
│       │   ├── routes/
│       │   │   ├── __root.tsx        # TanStack Router root layout
│       │   │   ├── index.tsx         # Login (/)
│       │   │   ├── dashboard.tsx     # Stats + clicks chart (/dashboard)
│       │   │   ├── links.tsx         # Links table + create/edit/delete (/links)
│       │   │   ├── settings.tsx      # Settings (/settings)
│       │   │   └── dev.tsx           # Dev tools — seed (/dev, dev-only)
│       │   ├── components/
│       │   │   ├── ui/               # shadcn/ui primitives
│       │   │   ├── layout/           # app-shell, sidebar, header
│       │   │   ├── dashboard/        # stats-cards, clicks-chart
│       │   │   └── links/            # link-form-dialog, delete-link-dialog
│       │   ├── hooks/                # use-stats, use-links, use-aggregate-clicks
│       │   └── lib/
│       │       ├── api.ts            # Typed API client (React Query)
│       │       ├── utils.ts          # cn() utility
│       │       └── feature-flags.tsx # Feature flag context
│       ├── index.html
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── biome.json
│       └── package.json              # pnpm
│
├── packages/
│   └── db/                           # Shared DB package (workspace member: snip-db)
│       ├── pyproject.toml            # name = "snip-db"
│       ├── alembic.ini               # script_location = src/snip_db/migrations
│       └── src/
│           └── snip_db/
│               ├── __init__.py       # re-export engine factory + models
│               ├── engine.py         # create_engine, session factory, get_session
│               ├── models/
│               │   ├── __init__.py   # re-export all models
│               │   ├── base.py       # DeclarativeBase + naming conventions
│               │   ├── link.py
│               │   ├── click_event.py
│               │   └── feature_flag.py
│               └── migrations/
│                   ├── __init__.py
│                   ├── env.py        # imports models, targets Base.metadata
│                   ├── script.py.mako
│                   └── versions/
│
├── dev/
│   ├── docker-compose.yml            # Postgres (+ future Pub/Sub emulator)
│   └── .env.example                  # Template for local dev secrets
│
├── terraform/                        # Deferred
├── .github/                          # Deferred
├── pyproject.toml                    # uv workspace root
├── .gitignore
└── PLAN.md
```

---

## Current Focus: Phases 0–3 (Local Dev + DB + Backend + Frontend)

> Later phases (Terraform, Worker, CI/CD, Appsmith, Email) are deferred until the core app works locally.

---

## Phase 0 — Local Dev Setup ✅

### 0.1 uv Workspace Root (`pyproject.toml`) ✅
```toml
[project]
name = "snip"
version = "0.1.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["apps/dashboard-backend", "packages/*"]
# Note: frontend excluded — it uses pnpm, not uv
```

### 0.2 Docker Compose (`dev/docker-compose.yml`) ✅
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: shortener
      POSTGRES_USER: shortener_app
      POSTGRES_PASSWORD: localdev
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### 0.3 Environment Template (`dev/.env.example`) ✅
```env
DATABASE_URL=postgresql+asyncpg://shortener_app:localdev@localhost:5432/shortener
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
ENVIRONMENT=development
```

### 0.4 .gitignore ✅
Standard Python + Node + Terraform + .env + __pycache__ + node_modules + dist + .venv + .terraform

### 0.5 Quick Start ✅
```bash
# Start Postgres
cd dev && docker compose up -d && cd ..

# DB package
cd packages/db && uv sync && cd ../..

# Run migrations
cd packages/db && uv run alembic upgrade head && cd ../..

# Backend
cd apps/dashboard-backend && uv sync && cp ../../dev/.env.example .env
uv run fastapi dev src/dashboard_backend/main.py --port 8080

# Frontend (separate terminal)
cd apps/dashboard-frontend && pnpm install && pnpm dev

# Seed dev data (once backend is running)
curl -X POST http://localhost:8080/dev/seed
```

---

## Phase 1 — Database Schema (`packages/db`) ✅

### 1.1 DB Package (`packages/db/pyproject.toml`) ✅
```toml
[project]
name = "snip-db"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    "greenlet",
]

[project.optional-dependencies]
pg = ["asyncpg>=0.29"]
psycopg = ["psycopg[binary]"]
test = ["pytest", "pytest-asyncio"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 1.2 Base Model (`src/snip_db/models/base.py`) ✅
SQLAlchemy 2.0 `DeclarativeBase` with `NAMING_CONVENTION` for constraints.

### 1.3 Models ✅
All use SQLAlchemy 2.0 `Mapped`/`mapped_column` style.

**Link** — id (UUID PK), org_id, short_code (unique), target_url, title, click_count, is_active, created_by, created_at, expires_at

**ClickEvent** — id (UUID PK), link_id (FK→links), clicked_at, user_agent, country

**FeatureFlag** — id (int PK), key (unique), enabled, description, updated_by, updated_at

### 1.4 Engine (`src/snip_db/engine.py`) ✅
- Module-level `_session_factory` pattern with `init_session_factory()` called during FastAPI lifespan
- `get_session` async generator for FastAPI `Depends()`
- Async engine from DATABASE_URL

### 1.5 Alembic ✅
- `alembic.ini` at package root, `script_location = src/snip_db/migrations`
- `env.py` imports all models, targets `Base.metadata`, converts async URL to psycopg for offline mode
- Initial migration: autogenerate from models
- Seed migration: insert 3 default feature flags (`analytics_dashboard`, `custom_short_codes`, `link_expiry`)

---

## Phase 2 — FastAPI Backend (`apps/dashboard-backend`) ✅

### 2.1 Dependencies (`pyproject.toml`) ✅
```toml
[project]
name = "dashboard-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "snip-db[pg]",
    "fastapi[standard]",
    "pydantic-settings",
    "httpx",
    "python-jose[cryptography]",
    "shortuuid",
]

[tool.uv.sources]
snip-db = { workspace = true }

[tool.ruff]
target-version = "py312"
line-length = 100
```

### 2.2 Config (`config.py`) ✅
Pydantic Settings: DATABASE_URL, CLERK_SECRET_KEY, ENVIRONMENT (default "development")

### 2.3 Clerk JWT Middleware (`clerk.py`) ✅
- Fetch JWKS from Clerk
- Validate Bearer token, extract org_id + user_id
- Dev bypass when ENVIRONMENT=development → returns `ClerkUser(user_id="dev_user", org_id="dev_org")`

### 2.4 Routers ✅

**Links** (`routers/links.py`):
```
POST   /links              — create link (title required, optional custom short code)
GET    /links              — list for org (paginated, search, sort, status filter)
GET    /links/{id}         — single link
PATCH  /links/{id}         — update (target_url, title, is_active)
DELETE /links/{id}         — soft delete (sets is_active=false)
```

**Redirect** (`routers/redirect.py`):
```
GET    /r/{short_code}     — public, 302 redirect, increment click_count, record ClickEvent
```

**Clicks** (`routers/clicks.py`):
```
GET    /links/{id}/clicks  — click_count + last 7 days daily breakdown
GET    /clicks/aggregate   — org-wide last 30 days daily breakdown
```

**Stats** (`routers/stats.py`):
```
GET    /stats              — total_links, total_clicks, active_links, expired_links
```

**Flags** (`routers/flags.py`):
```
GET    /flags              — {key: enabled} map, 60s in-memory TTL cache
```

**Seed** (`routers/seed.py`) — dev-only, conditionally mounted:
```
POST   /dev/seed           — seeds 25 links + weighted click events (dev env only)
```

### 2.5 Main (`main.py`) ✅
- FastAPI app with lifespan for DB init/teardown
- CORS for localhost:5173
- Seed router only mounted when `ENVIRONMENT=development`

---

## Phase 3 — Frontend (`apps/dashboard-frontend`) ✅

### 3.1 Stack ✅
- **Vite** — bundler + TanStack Router plugin
- **React 19** + **TypeScript**
- **TanStack Router** — file-based routing
- **TanStack Query (React Query)** — server state
- **shadcn/ui** — component library (dark mode default, teal-cyan brand)
- **Biome** — linting + formatting
- **Vitest** — testing (configured, tests TBD)
- **@clerk/react** — auth (v6, uses `<Show when="signed-in">`)
- **pnpm** — package manager
- **Recharts** — charts
- **Lucide React** — icons

### 3.2 Brand
- Primary color: teal-cyan `hsl(173 80% 50%)`
- Fonts: Inter (UI) + JetBrains Mono (code)
- Logo: scissors SVG (`snip-logo.tsx`)

### 3.3 Pages ✅

**Login** (`/`):
- Clerk `<SignIn />` component (skipped in dev mode)

**Dashboard** (`/dashboard`):
- 4 stat cards (total links, total clicks, active links, expired links)
- Area chart — aggregate clicks over 30 days
- Page scrolls normally

**Links** (`/links`):
- Full links table with search, sort (title/clicks/created), status filter (all/active/inactive/expired)
- "Create Link" button opens dialog (title required, URL required, optional custom short code)
- Kebab menu per row: Copy URL, Edit (dialog), Delete (confirmation dialog)
- Table scrolls within fixed height, sticky header, pagination pinned at bottom
- Page does not scroll

**Settings** (`/settings`):
- Placeholder

**Dev Tools** (`/dev`) — dev-only:
- Seed database button
- Redirects to `/dashboard` if not in dev mode

### 3.4 Layout ✅
- Fixed sidebar (w-60): Snip logo, nav (Dashboard, Links, Settings), dev section with Dev Tools link
- Header: mobile hamburger menu (Sheet), user avatar dropdown
- Full-height flex layout, each route controls its own scroll behavior

### 3.5 API Integration ✅
- Axios client with Clerk token injection
- React Query hooks: `useStats`, `useLinks` (with `keepPreviousData`), `useAggregateClicks`
- Feature flags via context provider (60s stale/refetch)
- Vite proxy: `/api` → `localhost:8080`

---

## Deferred Phases (Build Later)

The following phases from the original plan remain unchanged but are deferred:

- **Phase 4** — Terraform Infrastructure
- **Phase 5** — Click Worker (Pub/Sub → BigQuery)
- **Phase 6** — GitHub Actions CI/CD
- **Phase 7** — Appsmith Back Office
- **Phase 8** — Email (Resend)
- **Phase 9** — Validation Checklist

---

## Environment Variables Reference

| Variable | Where | Used by |
|---|---|---|
| `DATABASE_URL` | dev/.env.example | DB package, Backend |
| `CLERK_SECRET_KEY` | dev/.env.example | Backend |
| `CLERK_PUBLISHABLE_KEY` | dev/.env.example | Frontend |
| `ENVIRONMENT` | dev/.env.example | Backend |
| `VITE_API_URL` | Frontend .env | Frontend |
| `VITE_CLERK_PUBLISHABLE_KEY` | Frontend .env | Frontend |
