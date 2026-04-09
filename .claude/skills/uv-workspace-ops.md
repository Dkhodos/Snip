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

   [project.optional-dependencies]
   dev = ["pytest", "pytest-asyncio", "pytest-cov", "ruff", "pyright>=1.1.400"]

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"
   ```

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
	$(UV) sync --all-packages --extra dev
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

- **"No module named X"**: Run `uv sync --all-packages --extra dev` from repo root
- **Lock file conflicts**: Run `uv lock` to regenerate `uv.lock`
- **Stale venv**: Delete `.venv/` and `uv sync --all-packages` to rebuild
- **Missing workspace source**: Ensure both `dependencies` and `[tool.uv.sources]` entries exist
