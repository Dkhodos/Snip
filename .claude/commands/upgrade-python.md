---
name: upgrade-python
description: Upgrade Python version across the entire monorepo
---

# Upgrade Python Version

Step-by-step runbook for upgrading the Python version used across the Snip monorepo.

## Instructions

1. Ask the user for the **target Python version** (e.g., `3.13`).

2. Update all locations in this order:

### Step 1: `.python-version` (single source of truth for local dev + CI)

```
.python-version
```

Change the version number (e.g., `3.12` to `3.13`). CI workflows read this file via `python-version-file`.

### Step 2: Root `pyproject.toml`

```
pyproject.toml  →  requires-python = ">=3.XX"
```

### Step 3: All 14 member `pyproject.toml` files

Each member has three version references:

| Field | Section | Example |
|-------|---------|---------|
| `requires-python` | `[project]` | `">=3.12"` → `">=3.13"` |
| `target-version` | `[tool.ruff]` | `"py312"` → `"py313"` |
| `pythonVersion` | `[tool.pyright]` | `"3.12"` → `"3.13"` |

Files:
- `apps/dashboard-backend/pyproject.toml`
- `apps/redirect-service/pyproject.toml`
- `apps/click-worker/pyproject.toml`
- `packages/db/pyproject.toml`
- `packages/email/pyproject.toml`
- `packages/auth/pyproject.toml`
- `packages/logger/pyproject.toml`
- `packages/telemetry/pyproject.toml`
- `packages/queue/pyproject.toml`
- `packages/analytics/pyproject.toml`
- `packages/storage/pyproject.toml`
- `packages/og-image/pyproject.toml`
- `terraform/pyproject.toml` (only `requires-python`)
- `security/pyproject.toml` (only `requires-python`)

### Step 4: Base Docker image

```
.devops/images/python/Dockerfile  →  FROM python:X.Y-slim
```

This cannot read `.python-version` — Docker `FROM` requires a literal value.

### Step 5: Rebuild base images

Trigger the base images CI workflow or build locally. All app Dockerfiles inherit from this image.

### Step 6: Regenerate lockfile and sync

```bash
rm -rf .venv
uv lock
uv sync --all-packages --group dev
```

Deleting `.venv` ensures a clean environment on the new Python version.

### Step 7: Run lint and tests for all projects

```bash
make dashboard-backend:lint && make dashboard-backend:test:unit
make redirect-service:lint && make redirect-service:test:unit
make click-worker:lint && make click-worker:test:unit
make db:lint && make db:test:unit
make telemetry:lint && make telemetry:test:unit
# ... repeat for all projects
```

### Step 8: Review ruff ignore rules

Some `UP0xx` rules may become removable on newer Python versions:
- `UP006` (typing.List/Dict/Tuple) — removable on 3.9+
- `UP007` (Optional[X] → X | None) — removable on 3.10+
- `UP035` (typing imports) — removable on 3.9+
- `UP045` (Optional[X]) — removable on 3.10+

Check if these ignores can be dropped for the target version and run `ruff check --fix` to auto-migrate.

## Notes

- CI workflows do NOT need updating — they read `.python-version` automatically
- The `uv.lock` resolution markers will update to reflect the new Python floor
- If any dependency does not support the target Python version, `uv lock` will fail with a clear error
