# PLAN.md — B2B URL Shortener (Stack Validation Project)

> **Purpose:** A focused test project to validate the full startup stack before applying it to the real product.
> Build this end-to-end, in order. Each phase is independently deployable.

---

## Stack Being Validated

| Layer | Tool | Status |
|---|---|---|
| Compute | Cloud Run (Cloud Run Jobs for async) | Deferred |
| Frontend | Vite + React + TanStack Router → Cloud Run (nginx) | **Done (local)** |
| UI | shadcn/ui (dark mode) | **Done** |
| State | React Query (TanStack Query) | **Done** |
| Frontend Linting | Biome | **Done** |
| Frontend Type Checking | tsc | **Done** |
| Frontend Testing | Vitest | **Done** (78+ tests) |
| Backend | Python / FastAPI | **Done** |
| Backend Linting | Ruff | **Done** |
| Backend Type Checking | Pyright | **Done** |
| Backend Testing | pytest | **Done** (99% coverage) |
| Auth | Clerk (B2B orgs, native UI) | **Done** |
| Operational DB | Cloud SQL (Postgres) | **Done (local)** |
| ORM / Migrations | SQLAlchemy + Alembic | **Done** |
| Queue | Pub/Sub | Deferred |
| Analytics DB | BigQuery | Deferred |
| CI/CD | GitHub Actions | **Done (lint/type/test)** |
| Secrets | Infisical → GCP Secret Manager | Deferred |
| IaC | Terraform (state in GCS) | Deferred |
| Back Office | Appsmith (self-hosted on Cloud Run) | Deferred |
| Feature Flags | Cloud SQL table (managed via Appsmith) | **Done** |
| Error Tracking | Sentry | Deferred |
| Email | Resend | Deferred |
| CDN / DNS | Cloudflare DNS → Cloud Run frontend | Deferred |

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
│   │   │       ├── config.py         # Pydantic Settings
│   │   │       ├── dependencies.py   # DI wiring (stores, managers, auth)
│   │   │       ├── clients/
│   │   │       │   ├── auth_client.py    # AuthClient Protocol
│   │   │       │   ├── clerk_client.py   # Real Clerk JWT + JWKS
│   │   │       │   └── dev_auth_client.py # Dev bypass (fixed user/org)
│   │   │       ├── managers/
│   │   │       │   ├── link_manager.py
│   │   │       │   ├── clicks_manager.py
│   │   │       │   ├── redirect_manager.py
│   │   │       │   ├── feature_flag_manager.py
│   │   │       │   └── seed_manager.py
│   │   │       └── routers/
│   │   │           ├── __init__.py
│   │   │           ├── links.py
│   │   │           ├── redirect.py
│   │   │           ├── clicks.py
│   │   │           ├── flags.py
│   │   │           ├── stats.py
│   │   │           └── seed.py       # Dev-only, conditionally mounted
│   │   ├── tests/                    # 20 test files, 99% coverage
│   │   ├── Dockerfile
│   │   ├── Makefile
│   │   └── pyproject.toml            # depends on "snip-db[pg]"
│   │
│   └── dashboard-frontend/           # Vite SPA → Cloudflare Pages
│       ├── src/
│       │   ├── main.tsx              # ClerkProvider + QueryClient + Router
│       │   ├── globals.css           # Snip brand colors + fonts
│       │   ├── routes/
│       │   │   ├── __root.tsx        # Auth guards + OrgGuard + AppShell
│       │   │   ├── index.tsx         # Login (/)
│       │   │   ├── dashboard.tsx     # Stats + clicks chart (/dashboard)
│       │   │   ├── links.tsx         # Links table + create/edit/delete (/links)
│       │   │   ├── settings.tsx      # Org settings + members (/settings)
│       │   │   └── dev.tsx           # Dev tools — seed (/dev, dev-only)
│       │   ├── components/
│       │   │   ├── ui/               # shadcn/ui primitives (14 components)
│       │   │   ├── auth/             # auth-token-sync, org-guard
│       │   │   ├── layout/           # app-shell, sidebar, header
│       │   │   ├── dashboard/        # stats-cards, clicks-chart
│       │   │   ├── links/            # link-form-dialog, delete-link-dialog
│       │   │   └── org/              # org-switcher, org-avatar, create-org-form,
│       │   │                         # create-org-dialog, org-general-settings,
│       │   │                         # org-members, invite-member-dialog
│       │   ├── hooks/                # use-stats, use-links, use-aggregate-clicks
│       │   └── lib/
│       │       ├── api.ts            # Typed API client (axios + React Query)
│       │       ├── utils.ts          # cn() utility
│       │       ├── dev-mode.ts       # DEV_MODE constant (single source of truth)
│       │       └── feature-flags.tsx # Feature flag context
│       ├── index.html
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── biome.json
│       └── package.json              # pnpm
│
├── packages/
│   └── db/                           # Shared DB package (workspace member: snip-db)
│       ├── pyproject.toml            # name = "snip-db", Pyright configured
│       ├── alembic.ini               # script_location = src/snip_db/migrations
│       ├── Makefile
│       ├── tests/                    # 10 test files, 90%+ coverage
│       └── src/
│           └── snip_db/
│               ├── __init__.py       # re-export engine factory + models + stores
│               ├── engine.py         # create_engine, session factory, get_session
│               ├── models/
│               │   ├── __init__.py   # re-export all models
│               │   ├── base.py       # DeclarativeBase + naming conventions
│               │   ├── link.py
│               │   ├── click_event.py
│               │   └── feature_flag.py
│               ├── stores/
│               │   ├── __init__.py
│               │   ├── base_store.py     # Generic BaseStore[T] with session mgmt
│               │   ├── link_store.py     # Full CRUD + search/sort/pagination
│               │   ├── click_event_store.py  # Create + daily/aggregate queries
│               │   └── feature_flag_store.py # Get/update + cached dict
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
├── .github/
│   └── workflows/
│       ├── db.yml                    # packages/db: lint + type + test
│       ├── dashboard-backend.yml     # backend: lint + type + test
│       └── dashboard-frontend.yml    # frontend: lint + type + test + build
├── terraform/                        # Deferred
├── Makefile                          # Root monorepo delegation
├── pyproject.toml                    # uv workspace root
├── .gitignore
└── PLAN.md
```

---

## Current Focus: Phases 0–3 (Local Dev + DB + Backend + Frontend + Auth)

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
Postgres 15 with `shortener` DB, `shortener_app` user, port 5432.

### 0.3 Environment Template (`dev/.env.example`) ✅
```env
DATABASE_URL=postgresql+asyncpg://shortener_app:localdev@localhost:5432/shortener
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
ENVIRONMENT=development

# To run WITHOUT Clerk auth (dev bypass), leave the keys as pk_test_... / sk_test_...
# To run WITH Clerk auth locally, replace with real keys from https://dashboard.clerk.com
```

### 0.4 Quick Start ✅
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

### 1.1 Models ✅
All use SQLAlchemy 2.0 `Mapped`/`mapped_column` style with `DeclarativeBase` + naming conventions.

- **Link** — id (UUID PK), org_id, short_code (unique), target_url, title, click_count, is_active, created_by, created_at, expires_at
- **ClickEvent** — id (UUID PK), link_id (FK→links), clicked_at, user_agent, country
- **FeatureFlag** — id (int PK), key (unique), enabled, description, updated_by, updated_at

### 1.2 Engine ✅
Module-level `_session_factory` pattern, `init_session_factory()` called during FastAPI lifespan, `get_session` async generator for `Depends()`.

### 1.3 Stores ✅
Generic `BaseStore[T]` with session management. Concrete stores:
- **LinkStore** — Full CRUD, search, sort, pagination, stats
- **ClickEventStore** — Create, daily/aggregate queries, cleanup
- **FeatureFlagStore** — Get/update, cached dict (60s TTL)

### 1.4 Alembic ✅
Initial migration (autogenerate) + seed migration (3 default feature flags) + `multiple_orgs` flag migration.

---

## Phase 2 — FastAPI Backend (`apps/dashboard-backend`) ✅

### 2.1 Config (`config.py`) ✅
Pydantic Settings: `DATABASE_URL`, `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `ENVIRONMENT`.

### 2.2 Auth Client Layer ✅
- **AuthClient Protocol** — Swappable auth abstraction
- **ClerkClient** — Real Clerk JWT + JWKS validation, extracts `user_id` and `org_id`, rejects 403 if `org_id` missing
- **DevAuthClient** — Dev bypass returning fixed user/org
- Dependency injection via `dependencies.py`

### 2.3 Manager Layer ✅
Business logic decoupled from HTTP routing:
- **LinkManager** — Create, list (filtering/search/sort), get, update, delete
- **ClicksManager** — Daily and aggregate click queries
- **RedirectManager** — Handle redirect + record click
- **FeatureFlagManager** — Get flags with caching
- **SeedManager** — Development data seeding

### 2.4 Routers ✅

| Router | Endpoints |
|---|---|
| **Links** | `POST /links` (title required, optional custom short code), `GET /links` (paginated, search, sort, status filter), `GET /links/{id}`, `PATCH /links/{id}`, `DELETE /links/{id}` (soft delete) |
| **Redirect** | `GET /r/{short_code}` (302, increment click_count, record ClickEvent) |
| **Clicks** | `GET /links/{id}/clicks` (7-day breakdown), `GET /clicks/aggregate` (30-day org-wide) |
| **Stats** | `GET /stats` (total_links, total_clicks, active_links, expired_links) |
| **Flags** | `GET /flags` ({key: enabled} map, 60s TTL cache) |
| **Seed** | `POST /dev/seed` (dev-only, conditionally mounted, 25 links + click events) |

### 2.5 Main (`main.py`) ✅
FastAPI app with lifespan (DB init/teardown), CORS for localhost:5173, seed router only mounted in development. Health check endpoint at `GET /health`.

---

## Phase 3 — Frontend (`apps/dashboard-frontend`) ✅

### 3.1 Stack ✅
- **Vite** + TanStack Router plugin
- **React 19** + **TypeScript**
- **TanStack Router** — file-based routing
- **TanStack Query** — server state
- **shadcn/ui** — 14 components (button, card, input, table, badge, skeleton, dropdown-menu, separator, tooltip, avatar, sheet, scroll-area, dialog, alert-dialog)
- **Biome** — linting + formatting
- **Vitest** — testing (configured, tests TBD)
- **@clerk/react** v6 — auth (Clerk hooks for org management, native UI)
- **pnpm** — package manager
- **Recharts** — charts
- **Lucide React** — icons

### 3.2 Brand ✅
- Primary: teal-cyan `hsl(173 80% 50%)`
- Fonts: Inter (UI) + JetBrains Mono (code)
- Logo: scissors SVG (`snip-logo.tsx`)
- Dark mode default

### 3.3 Auth & Organization Flow ✅

**Dev bypass** (`src/lib/dev-mode.ts`):
- Single source of truth: `DEV_MODE = !CLERK_KEY || CLERK_KEY === "pk_test_..."`
- When active: skips ClerkProvider, OrgGuard, org switcher; uses static "Dev Org"

**Auth flow** (with real Clerk keys):
1. Unauthenticated → `<RedirectToSignIn />` (Clerk hosted sign-in)
2. Authenticated, no org → `OrgGuard` shows native create-org form (name + slug)
3. Authenticated, has org → dashboard with data scoped to active org

**Token sync** (`auth-token-sync.tsx`):
- `useAuth().getToken({ skipCache: true })` on org change
- Injects Bearer token into axios via `setAuthToken()`
- Invalidates all React Query caches on org switch
- Refreshes every 50s

**Organization management** (all native shadcn/ui, no Clerk pre-built components):

| Component | Location | Description |
|---|---|---|
| `OrgGuard` | `components/auth/` | Blocks access until org exists; shows create-org form |
| `OrgSwitcher` | `components/org/` | Dropdown in sidebar: current org, list all, switch, create new |
| `OrgAvatar` | `components/org/` | Avatar with initials fallback, reused across org UI |
| `CreateOrgForm` | `components/org/` | Name + auto-slugified slug, calls `createOrganization` + `setActive` |
| `CreateOrgDialog` | `components/org/` | Dialog wrapper around CreateOrgForm (triggered from switcher) |
| `OrgGeneralSettings` | `components/org/` | Edit org name/slug (admin only) |
| `OrgMembers` | `components/org/` | Members table with roles, remove (admin), pending invitations |
| `InviteMemberDialog` | `components/org/` | Invite by email with role picker (Member/Admin) |

### 3.4 Pages ✅

**Login** (`/`):
- Clerk sign-in (skipped in dev mode → straight to dashboard)

**Dashboard** (`/dashboard`):
- 4 stat cards (total links, total clicks, active links, expired links)
- Area chart — aggregate clicks over 30 days

**Links** (`/links`):
- Full links table with search, sort, status filter, pagination
- Create Link dialog (title required, URL required, optional custom short code)
- Kebab menu: Copy URL, Edit (dialog), Delete (confirmation)
- Table scrolls within fixed height, sticky header

**Settings** (`/settings`):
- Org general settings card (name, slug — editable for admins)
- Members card (table with roles, remove, invite)
- In dev mode: placeholder message

**Dev Tools** (`/dev`) — dev-only:
- Seed database button
- Redirects to `/dashboard` if not in dev mode

### 3.5 Layout ✅
- Fixed sidebar (w-60): Snip logo → org switcher → nav (Dashboard, Links, Settings) → dev section
- Header: mobile hamburger menu (Sheet), user avatar dropdown (Settings, Sign Out)
- Full-height flex layout, each route controls its own scroll behavior

### 3.6 API Integration ✅
- Axios client with Clerk token injection (Bearer)
- React Query hooks: `useStats`, `useLinks` (with `keepPreviousData`), `useAggregateClicks`
- Feature flags via context provider (60s stale/refetch)
- Vite proxy: `/api` → `localhost:8080`

---

## Phase 6 — GitHub Actions CI/CD ✅ (Lint/Type/Test)

Three workflows with path-based triggers and `cancel-in-progress` concurrency:

| Workflow | Triggers | Steps |
|----------|----------|-------|
| `db.yml` | `packages/db/**`, `uv.lock` | Ruff lint, Pyright, pytest |
| `dashboard-backend.yml` | `apps/dashboard-backend/**`, `packages/db/**` | Ruff lint, Pyright, pytest |
| `dashboard-frontend.yml` | `apps/dashboard-frontend/**` | Biome lint, tsc, Vitest, Vite build |

Root `Makefile` delegates to sub-project Makefiles for unified commands.

> Deployment CI (Cloud Run, Cloudflare Pages) deferred to Phase 4 (Terraform).

---

## Deferred Phases (Build Later)

- **Phase 4** — Terraform Infrastructure
- **Phase 5** — Click Worker (Pub/Sub → BigQuery)
- **Phase 7** — Appsmith Back Office
- **Phase 8** — Email (Resend)
- **Phase 9** — Validation Checklist

---

## Environment Variables Reference

| Variable | Where | Used by |
|---|---|---|
| `DATABASE_URL` | Backend .env | DB package, Backend |
| `CLERK_PUBLISHABLE_KEY` | Backend .env | Backend (JWKS URL derivation) |
| `CLERK_SECRET_KEY` | Backend .env | Backend (dev bypass check) |
| `ENVIRONMENT` | Backend .env | Backend (dev mode, seed router) |
| `VITE_CLERK_PUBLISHABLE_KEY` | Frontend .env.local | Frontend (ClerkProvider, DEV_MODE) |
| `VITE_API_URL` | Frontend .env.local | Frontend (API base URL, optional) |
