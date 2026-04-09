# Snip

URL shortener monorepo: FastAPI backends, React frontend, shared Python packages, Terraform infra.

## Monorepo Layout

```
apps/                          # Deployable services
  dashboard-backend/           # FastAPI — link CRUD, stats, OG images
  dashboard-frontend/          # Vite + React + TanStack Router
  redirect-service/            # FastAPI — short URL resolution
  click-worker/                # Pub/Sub click event processor
  e2e/                         # Playwright E2E tests

packages/                      # Shared Python libraries (Provider Pattern)
  auth/    db/    email/    logger/    queue/
  analytics/    storage/    og-image/

terraform/                     # Terragrunt + Terraform (GCP)
dev/                           # docker-compose for local services
```

## UV Workspace

Root `pyproject.toml` defines the workspace. Members: all apps (except `dashboard-frontend` and `e2e`) and all packages.

- **Package pip name**: `<project>-<name>` (e.g., `<project>-auth`)
- **Package import name**: `<project>_<name>` (e.g., `<project>_auth`)
- **App import name**: `<name_underscore>` (e.g., `dashboard_backend`, `redirect_service`)
- **Workspace source reference** in pyproject.toml: `<project>-<name> = { workspace = true }`
- **Build system**: hatchling for all packages and apps

## Make Commands

Always run from repo root using `make <project>:<target>`:

```bash
make dashboard-backend:lint        # ruff check + format --check + pyright
make dashboard-backend:lint:fix    # ruff check --fix + format
make dashboard-backend:type:check  # pyright only
make dashboard-backend:test:unit   # pytest with 90% coverage threshold
make dashboard-backend:dev         # uvicorn with hot reload
make dashboard-frontend:dev        # vite dev server
make db:lint                       # lint the db package
make db:test:unit                  # test the db package
```

Run `make <project>:help` to see all targets for a project.

## Dev Environment

```bash
# Start local services (Postgres, Mailpit, MinIO)
docker compose -f dev/docker-compose.yml up -d

# Each app has its own .env file — copy from .env.example
cp apps/dashboard-backend/.env.example apps/dashboard-backend/.env
```

## Pre-Commit Checklist

Before every commit, run lint and tests for all affected projects:

```bash
make <project>:lint
make <project>:test:unit
```

## Coverage Threshold

All Python projects enforce **90% test coverage** (`--cov-fail-under=90`).

## Python Tooling

- **Ruff** for linting and formatting (line-length 100, select E/F/I/UP/B/SIM)
- **Pyright** for type checking (standard mode)
- **pytest** + pytest-asyncio for testing (asyncio_mode = "auto")
- **SQLite (aiosqlite)** for test databases — per-test transactional rollback

## Frontend Tooling

- **Biome** for linting and formatting (tab indentation, not ESLint/Prettier)
- **TypeScript** strict mode with `noUncheckedIndexedAccess`
- **Vitest** + Testing Library for unit tests
- **Playwright** for E2E tests (in `apps/e2e/`)

## Key Conventions

- **Backend layering**: Router -> Manager -> Store (see `.claude/rules/backend-conventions.md`)
- **Package pattern**: Protocol + StrEnum + Factory (see `.claude/rules/package-conventions.md`)
- **Frontend pattern**: thin routes, page components, custom hooks (see `.claude/rules/frontend-conventions.md`)
- **No `console.log`** in frontend production code
- **No `print()`** in backend code — use the `<project>_logger` package
