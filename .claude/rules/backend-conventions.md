# Backend Conventions (FastAPI Apps)

Applies to: `apps/dashboard-backend/`, `apps/redirect-service/`, `apps/click-worker/`

## App Structure

```
apps/<name>/
  src/<import_name>/
    __init__.py
    main.py              # FastAPI app, lifespan, middleware, exception handlers, router includes
    config.py            # pydantic_settings.BaseSettings singleton
    cli.py               # Entry points for dev/serve scripts (uvicorn.run wrappers)
    dependencies.py      # All FastAPI Depends wiring
    exceptions.py        # DomainError hierarchy
    routers/             # One file per resource — APIRouter with prefix and tags
      __init__.py
    managers/            # Business logic classes
      __init__.py
  tests/
    __init__.py
    conftest.py          # Session-scoped engine, per-test transactional rollback
    unit/
      __init__.py
      base/              # BaseDBTestCase, BaseApiTestCase
      routers/           # One test file per router
      managers/          # One test file per manager
```

Import name is the directory name under `src/` (e.g., `dashboard_backend`, `redirect_service`).

## Layered Architecture

```
Router  →  Manager  →  Store (from <project>-db)
  │           │           │
  │           │           └─ Data access (SQLAlchemy queries)
  │           └─ Business logic, validation, orchestration
  └─ HTTP concerns: request/response models, status codes, DI wiring
```

- Routers **never** call stores directly
- Managers **never** import FastAPI types (no Request, Response, HTTPException)
- Managers raise **DomainError** subclasses; routers map them to HTTP status codes via exception handlers in `main.py`

## Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = ""
    environment: str = "development"
    # ... all env vars as fields with defaults

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()  # module-level singleton
```

## Dependency Injection (`dependencies.py`)

All DI wiring lives in `dependencies.py`. Pattern:

```python
def get_<store>(session: AsyncSession = Depends(get_session)) -> <Store>:
    return <Store>(session)

def get_<manager>(<store>: <Store> = Depends(get_<store>)) -> <Manager>:
    return <Manager>(<store>)

async def get_current_user(request: Request, auth_client: AuthClient = Depends(get_auth_client)) -> AuthUser:
    # token extraction and verification
```

Dev bypass: when `environment == "development"` and no real auth keys configured, use `AuthProvider.DEV`.

## Exception Handling (`exceptions.py`)

```python
class DomainError(Exception):
    """Base class for all domain exceptions."""

class LinkNotFoundError(DomainError):
    def __init__(self, detail: str = "Link not found") -> None:
        super().__init__(detail)
        self.detail = detail
```

In `main.py`, register exception handlers that map domain errors to HTTP responses:

```python
@app.exception_handler(LinkNotFoundError)
async def link_not_found_handler(request: Request, exc: LinkNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})
```

**Never** raise `HTTPException` from managers.

## Router Patterns (`routers/*.py`)

```python
router = APIRouter(prefix="/links", tags=["links"])

# Request/response models defined inline as Pydantic BaseModel
class CreateLinkRequest(BaseModel):
    target_url: str
    title: str

class LinkResponse(BaseModel):
    id: UUID
    short_code: str
    # ...
    model_config = {"from_attributes": True}  # ORM compatibility

class LinkListResponse(BaseModel):
    items: list[LinkResponse]
    total: int
    page: int
    limit: int

@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(
    body: CreateLinkRequest,
    user: AuthUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> object:
    return await manager.create_link(org_id=user.org_id, ...)
```

- Request/response models defined **in the router file**, not in a shared models module
- List responses use the envelope pattern: `{items, total, page, limit}`
- Response models use `model_config = {"from_attributes": True}` for ORM objects

## Manager Patterns (`managers/*.py`)

```python
class LinkManager:
    def __init__(self, link_store: LinkStore) -> None:
        self._link_store = link_store

    async def create_link(self, *, org_id: str, ...) -> Link:
        # business logic
        link = await self._link_store.create(...)
        await self._link_store.commit()
        _log.info("link_created", short_code=short_code, org_id=org_id)
        return link
```

- Constructor receives stores (injected via DI)
- Use keyword-only arguments (`*`) for clarity
- Commit via the store after mutations
- Log structured key-value pairs

## Logging

```python
from <project>_logger import get_logger

_log = get_logger("service-name", log_prefix="ClassName")
_log.info("event_name", key=value, other_key=other_value)
```

## Entry Points (`cli.py`)

Apps define `[project.scripts]` in their `pyproject.toml` for dev and serve entry points:

```toml
[project.scripts]
dashboard-dev = "dashboard_backend.cli:dev"
dashboard-serve = "dashboard_backend.cli:serve"
```

The `cli.py` module wraps `uvicorn.run()` with two configurations:

```python
import uvicorn

def dev() -> None:
    """Dev server with hot reload on an app-specific port."""
    uvicorn.run("dashboard_backend.main:app", host="0.0.0.0", port=8001, reload=True)

def serve() -> None:
    """Production server on port 8080."""
    uvicorn.run("dashboard_backend.main:app", host="0.0.0.0", port=8080)
```

- Makefile `dev` target: `$(UV) run --package <pip-name> <short-name>-dev`
- `entrypoint.sh` in the Docker image calls the serve script

## Application Lifespan (`main.py`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging(is_local=settings.environment == "development")
    engine = create_engine(settings.effective_database_url)
    session_factory = create_session_factory(engine)
    init_session_factory(session_factory)
    yield
    await engine.dispose()
```

## Testing

- **conftest.py**: session-scoped SQLite engine, per-test connection with rollback, session with SAVEPOINT
- **Base classes**: `BaseDBTestCase` (provides `_db_session`), `BaseApiTestCase` (provides `AsyncClient`)
- Test files mirror source structure: `tests/unit/routers/test_links.py`, `tests/unit/managers/test_link_manager.py`
- 90% coverage threshold enforced

## Tooling

- Ruff: line-length 100, select `["E", "F", "I", "UP", "B", "SIM"]`
- Ruff ignore: `B008` (Depends in defaults), `UP006/UP007/UP035/UP045` (typing compat)
- Pyright: standard mode, exclude tests
- pytest-asyncio: `asyncio_mode = "auto"`
