---
name: fastapi-app-anatomy
description: Deep reference for building a FastAPI app in this monorepo — lifespan, middleware, routers, managers, DI, testing
---

# FastAPI App Anatomy

Complete walkthrough of how a FastAPI app is structured, using `dashboard-backend` as the canonical example.

## 1. Application Entry (`main.py`)

The app is created at module level. The lifespan context manager initializes the DB engine and session factory.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from <project>_db.engine import create_engine, create_session_factory, init_session_factory
from <project>_logger import configure_logging, logging_middleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging(is_local=settings.environment == "development")
    engine = create_engine(settings.effective_database_url)
    session_factory = create_session_factory(engine)
    init_session_factory(session_factory)
    yield
    await engine.dispose()

app = FastAPI(title="Service Name", version="0.1.0", lifespan=lifespan)

# Middleware order matters — outermost first
app.middleware("http")(logging_middleware)
app.add_middleware(CORSMiddleware, ...)

# Exception handlers — one per domain error
@app.exception_handler(LinkNotFoundError)
async def link_not_found_handler(request: Request, exc: LinkNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})

# Router registration
app.include_router(links.router)
app.include_router(stats.router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

**Key points:**
- Logging middleware is registered first (outermost) so it wraps everything
- CORS origins come from `settings.allowed_origins` (comma-separated string)
- Each domain exception gets its own handler — never use a catch-all
- Health check endpoint at `/health` (required for Cloud Run)

## 2. Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = ""
    db_host: str = ""
    db_port: int = 5432
    environment: str = "development"
    allowed_origins: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def effective_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
```

**Key points:**
- Module-level singleton — imported as `from <app>.config import settings`
- `extra = "ignore"` prevents errors from unrecognized env vars
- `effective_database_url` property handles both Cloud Run (full URL) and local dev (components)

## 3. Dependency Injection (`dependencies.py`)

```python
# Auth
def get_auth_client() -> AuthClient:
    if _is_dev_bypass():
        return create_auth_client(AuthProvider.DEV)
    return create_auth_client(AuthProvider.CLERK, publishable_key=settings.clerk_publishable_key)

async def get_current_user(request: Request, auth_client: AuthClient = Depends(get_auth_client)) -> AuthUser:
    # Extract Bearer token, verify, return AuthUser

# Stores (one per DB table/resource)
def get_link_store(session: AsyncSession = Depends(get_session)) -> LinkStore:
    return LinkStore(session)

# Managers (one per business domain)
def get_link_manager(link_store: LinkStore = Depends(get_link_store)) -> LinkManager:
    return LinkManager(link_store)
```

**Chain:** `get_session` -> `get_<store>` -> `get_<manager>` -> injected into router endpoints.

## 4. Router Pattern

```python
router = APIRouter(prefix="/links", tags=["links"])

# Request models — defined here, not in a shared module
class CreateLinkRequest(BaseModel):
    target_url: str
    title: str

# Response models — from_attributes for ORM compatibility
class LinkResponse(BaseModel):
    id: UUID
    short_code: str
    model_config = {"from_attributes": True}

# List envelope
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

**Key points:**
- Return type is `object` (not the response model) — FastAPI handles serialization
- All endpoints require `get_current_user` for auth
- Org scoping via `user.org_id` passed to manager

## 5. Manager Pattern

```python
class LinkManager:
    def __init__(self, link_store: LinkStore) -> None:
        self._link_store = link_store

    async def create_link(self, *, org_id: str, user_id: str, target_url: str, title: str) -> Link:
        # Business logic here
        link = await self._link_store.create(...)
        await self._link_store.commit()
        _log.info("link_created", short_code=short_code, org_id=org_id)
        return link
```

**Key points:**
- Keyword-only args (`*`) for method signatures
- Commit through the store
- Raise DomainError subclasses, never HTTPException
- Log with structured key-value pairs

## 6. Testing Setup (`tests/conftest.py`)

```python
_TEST_DATABASE_URL = "sqlite+aiosqlite://"

@pytest.fixture(scope="session")
async def _engine():
    engine = create_async_engine(_TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture()
async def _db_connection(_engine):
    async with _engine.connect() as connection:
        transaction = await connection.begin()
        yield connection
        await transaction.rollback()

@pytest.fixture()
async def _db_session(_db_connection):
    session_factory = async_sessionmaker(
        bind=_db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    async with session_factory() as session:
        yield session
```

**Key points:**
- In-memory SQLite for speed — no real Postgres needed for unit tests
- Session-scoped engine (created once), per-test connection with rollback
- `join_transaction_mode="create_savepoint"` allows store `.commit()` calls without escaping the test transaction
