"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from snip_db.engine import create_engine, create_session_factory, init_session_factory

from dashboard_backend.config import settings
from dashboard_backend.exceptions import (
    AuthenticationError,
    InvalidSortFieldError,
    LinkExpiredError,
    LinkNotFoundError,
    OrganizationRequiredError,
    ShortCodeCollisionError,
)
from dashboard_backend.routers import clicks, flags, links, redirect, stats


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: set up and tear down DB engine."""
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    init_session_factory(session_factory)

    yield

    await engine.dispose()


app = FastAPI(title="Snip Dashboard API", version="0.1.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Domain exception handlers ---


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": exc.detail})


@app.exception_handler(OrganizationRequiredError)
async def organization_required_handler(
    request: Request, exc: OrganizationRequiredError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.detail})


@app.exception_handler(LinkNotFoundError)
async def link_not_found_handler(request: Request, exc: LinkNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(LinkExpiredError)
async def link_expired_handler(request: Request, exc: LinkExpiredError) -> JSONResponse:
    return JSONResponse(status_code=410, content={"detail": exc.detail})


@app.exception_handler(ShortCodeCollisionError)
async def short_code_collision_handler(
    request: Request, exc: ShortCodeCollisionError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(InvalidSortFieldError)
async def invalid_sort_field_handler(request: Request, exc: InvalidSortFieldError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.detail})


# Routers
app.include_router(links.router)
app.include_router(redirect.router)
app.include_router(clicks.router)
app.include_router(flags.router)
app.include_router(stats.router)

# Dev-only routers — only mounted when ENVIRONMENT=development
if settings.environment == "development":
    from dashboard_backend.routers import seed

    app.include_router(seed.router, prefix="/dev")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
