---
name: new-api-resource
description: Scaffold a new API resource end-to-end (backend + frontend)
---

# Scaffold New API Resource (End-to-End)

Create a complete API resource spanning backend and frontend.

## Instructions

1. Ask the user for:
   - **Resource name** (singular, e.g., `invoice`, `team-member`)
   - **Backend app** (e.g., `dashboard-backend`)
   - **Fields** (name + type pairs for the model)
   - **Operations** (CRUD subset: list, get, create, update, delete)

2. **Backend** — in `apps/<backend-app>/`:

   a. **Router** (`src/<import>/routers/<resource>.py`):
      - `APIRouter(prefix="/<resources>", tags=["<resources>"])`
      - Request/response Pydantic models inline
      - List endpoint with envelope `{items, total, page, limit}`
      - Response model with `model_config = {"from_attributes": True}`

   b. **Manager** (`src/<import>/managers/<resource>_manager.py`):
      - Constructor takes store via DI
      - Business logic methods, keyword-only args
      - Raises DomainError subclasses

   c. **Exceptions** — add to `exceptions.py`:
      - `<Resource>NotFoundError(DomainError)` with `.detail`

   d. **Exception handler** — register in `main.py`

   e. **Dependencies** — add to `dependencies.py`:
      - `get_<resource>_store()` and `get_<resource>_manager()`

   f. **Router registration** — add `app.include_router(<resource>.router)` in `main.py`

   g. **Tests**:
      - `tests/unit/routers/test_<resource>.py`
      - `tests/unit/managers/test_<resource>_manager.py`

3. **Frontend** — in `apps/dashboard-frontend/`:

   a. **API class** (`src/lib/api/<Resource>Api.ts`):
      - Extends `BaseApi`
      - Methods matching backend operations

   b. **Types** — add to `src/lib/api/types.ts`:
      - Request/response interfaces matching backend models

   c. **Export** — add singleton to `src/lib/api/index.ts`

   d. **Hook** (if page exists) (`src/pages/<Feature>/hooks/use<Resources>.ts`):
      - Wraps `useQuery`/`useMutation`

4. Run lint and tests for both projects.

## Reference

Follow the existing `links` resource as the canonical example:
- Backend: `routers/links.py`, `managers/link_manager.py`
- Frontend: `LinksApi.ts`, `pages/Links/hooks/useLinks.ts`
