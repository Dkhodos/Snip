---
name: new-backend-app
description: Scaffold a new FastAPI backend app following project conventions
---

# Scaffold New FastAPI Backend App

Create a new FastAPI app following the conventions in `.claude/rules/backend-conventions.md`.

## Instructions

1. Ask the user for:
   - **App name** (kebab-case, e.g., `billing-service`)
   - **Description** (one-line purpose)

2. Derive names:
   - Directory: `apps/<app-name>/`
   - Import name: `<app_name>` (underscores, e.g., `billing_service`)
   - Pip name: `<app-name>` (as-is)

3. Create the following files:

```
apps/<app-name>/
  src/<import_name>/
    __init__.py          # Empty
    main.py              # FastAPI app with lifespan, health check, CORS
    cli.py               # Entry points for dev/serve scripts (uvicorn.run wrappers)
    config.py            # Settings(BaseSettings) with env_file=".env", extra="ignore"
    dependencies.py      # get_current_user, placeholder stores/managers
    exceptions.py        # DomainError base class
    routers/
      __init__.py        # Empty
    managers/
      __init__.py        # Empty
  tests/
    __init__.py
    conftest.py          # Session-scoped SQLite engine, per-test rollback (copy pattern from dashboard-backend)
    unit/
      __init__.py
      base/
        __init__.py
        base_test_case.py
  pyproject.toml         # Copy structure from dashboard-backend; include [project.scripts] for dev/serve entry points; dev deps come from root [dependency-groups]
  Makefile               # Copy from dashboard-backend, adjust SRC and package name
  Dockerfile             # Copy from dashboard-backend, adjust entry point
  entrypoint.sh          # Docker entry point — calls the serve script
  .env.example           # Minimal env vars
```

4. Add entry to root `Makefile` PROJECTS list
5. Add to root `pyproject.toml` workspace members if not covered by glob
6. Define `<short-name>-dev` and `<short-name>-serve` scripts in `[project.scripts]` pointing to `<import_name>.cli:dev` and `<import_name>.cli:serve`
7. Run `uv sync --all-packages` to verify it resolves
8. Run `make <app-name>:lint` to verify the scaffold passes lint

## Reference

Use `apps/dashboard-backend/` as the canonical example. Copy patterns exactly — do not invent new conventions.
