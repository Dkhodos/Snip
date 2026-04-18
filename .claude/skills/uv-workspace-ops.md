---
name: uv-workspace-ops
description: Reference for UV workspace operations — adding members, dependencies, running scoped commands, Makefile patterns
---

# UV Workspace Operations

## Workspace Configuration

Root `pyproject.toml`:

```toml
[project]
name = "<project>"
version = "0.1.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["apps/dashboard-backend", "apps/redirect-service", "apps/click-worker", "packages/*", "terraform"]
```

- `packages/*` glob covers all packages automatically
- Apps must be listed explicitly (not all directories under `apps/` are UV members — `dashboard-frontend` and `e2e` are Node.js)
- Single shared venv at repo root: `.venv/`

## Adding a New Package

1. Create `packages/<name>/pyproject.toml`:
   ```toml
   [project]
   name = "<project>-<name>"
   version = "0.1.0"
   requires-python = ">=3.12"
   dependencies = [...]

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"
   ```

   Dev dependencies (pytest, ruff, pyright, etc.) come from the root `[dependency-groups] dev`. Only add a member-level `[dependency-groups] dev` if the package has extra test-only deps beyond the common set (e.g., `aiosqlite` for database packages).

2. The `packages/*` glob in root pyproject.toml picks it up automatically.

3. Run `uv sync --all-packages` to resolve and install.

## Adding a New App

1. Create `apps/<name>/pyproject.toml` (same structure as packages, different name pattern).

2. Add to root `pyproject.toml` workspace members:
   ```toml
   members = ["apps/dashboard-backend", "apps/redirect-service", "apps/click-worker", "apps/<name>", "packages/*", "terraform"]
   ```

3. Run `uv sync --all-packages`.

## Adding Dependencies

### External dependency
```bash
# From the package/app directory:
uv add <package-name>

# Or edit pyproject.toml directly and run:
uv sync --all-packages
```

### Workspace dependency (another project package)
In the consuming package's `pyproject.toml`:

```toml
[project]
dependencies = [
    "<project>-db[pg]",
    "<project>-auth",
]

[tool.uv.sources]
<project>-db = { workspace = true }
<project>-auth = { workspace = true }
```

Both `dependencies` AND `[tool.uv.sources]` entries are required.

## Running Commands Scoped to a Package

```bash
# Run a command in a specific package's context
uv run --package dashboard-backend python -m dashboard_backend
uv run --package dashboard-backend pytest tests/
uv run --package dashboard-backend ruff check src/

# Shorthand via Makefile
make dashboard-backend:test:unit
make db:lint
```

## Makefile Pattern

Each project has a Makefile that uses `uv run --package <name>` for all commands:

```makefile
ROOT     := $(shell git rev-parse --show-toplevel)
VENV     := $(ROOT)/.venv
UV       := uv
PYTHON   := $(UV) run --package <pip-name> python
PYTEST   := $(UV) run --package <pip-name> pytest
RUFF     := $(UV) run --package <pip-name> ruff
PYRIGHT  := $(UV) run --package <pip-name> pyright

# Sentinel for auto-sync
SYNC_STAMP := $(VENV)/.<pip-name>-synced

$(SYNC_STAMP): pyproject.toml $(ROOT)/uv.lock | $(VENV)/bin/python
	$(UV) sync --all-packages --group dev
	@touch $(SYNC_STAMP)

sync: $(SYNC_STAMP)

lint: sync
	$(RUFF) check $(SRC) $(TESTS)
	$(RUFF) format --check $(SRC) $(TESTS)
	$(PYRIGHT) $(SRC)

test\:unit: sync
	$(PYTEST) $(TESTS) --cov=$(SRC) --cov-report=term-missing --cov-fail-under=90 -v
```

**Sentinel stamp pattern:** The `SYNC_STAMP` file is touched after a successful `uv sync`. Make only re-syncs when `pyproject.toml` or `uv.lock` is newer than the stamp — making `sync` a fast no-op in the common case.

## Root Makefile Delegation

The root Makefile delegates to sub-project Makefiles:

```makefile
PROJECTS := \
    dashboard-backend:apps/dashboard-backend \
    db:packages/db \
    auth:packages/auth \
    ...
```

Usage: `make <project>:<target>` (e.g., `make dashboard-backend:lint`).

When adding a new project, add an entry to `PROJECTS` in the root Makefile.

## Common Issues

- **"No module named X"**: Run `uv sync --all-packages --group dev` from repo root
- **Lock file conflicts**: Run `uv lock` to regenerate `uv.lock`
- **Stale venv**: Delete `.venv/` and `uv sync --all-packages` to rebuild
- **Missing workspace source**: Ensure both `dependencies` and `[tool.uv.sources]` entries exist

## Additional Workspace Patterns

### `[dependency-groups]` — Centralized Dev Dependencies

The root `pyproject.toml` defines a `[dependency-groups] dev` section containing common dev dependencies (pytest, ruff, pyright, etc.) shared across all workspace members. Individual members only add a `[dependency-groups] dev` section if they need extra test-only deps beyond the common set (e.g., `aiosqlite` for database packages).

### `[tool.uv.constraint-dependencies]` — Version Floors

The root `pyproject.toml` has a `[tool.uv.constraint-dependencies]` section that enforces minimum version floors across the entire workspace. This ensures all members resolve to at least the specified versions without requiring each member to duplicate version constraints.

### `[project.scripts]` — App Entry Points

Apps define `<short-name>-dev` and `<short-name>-serve` entry points in their `[project.scripts]` section (e.g., `dashboard-dev`, `dashboard-serve`). These point to functions in a `cli.py` module that wraps `uvicorn.run()` with dev (reload, app-specific port) and prod (port 8080) configurations. Makefile `dev` targets use `$(UV) run --package <name> <short-name>-dev`.

### `.python-version` — Python Version Source of Truth

The `.python-version` file at the repo root is the single source of truth for the Python version used across the workspace. UV reads this file to determine which Python interpreter to use.
