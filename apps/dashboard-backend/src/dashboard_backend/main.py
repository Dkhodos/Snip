"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from snip_auth import AuthenticationError, OrganizationRequiredError
from snip_db.engine import create_engine, create_session_factory, init_session_factory
from snip_logger import configure_logging, logging_middleware

from dashboard_backend.config import settings
from dashboard_backend.exceptions import (
    InvalidSortFieldError,
    LinkNotFoundError,
    ShortCodeCollisionError,
)
from dashboard_backend.routers import clicks, flags, links, stats


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: set up and tear down DB engine."""
    configure_logging(is_local=settings.environment == "development")
    engine = create_engine(settings.effective_database_url)
    session_factory = create_session_factory(engine)
    init_session_factory(session_factory)

    yield

    await engine.dispose()


app = FastAPI(title="Snip Dashboard API", version="0.1.0", lifespan=lifespan)

# Logging middleware (outermost — registered first so it wraps everything)
app.middleware("http")(logging_middleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
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
app.include_router(clicks.router)
app.include_router(flags.router)
app.include_router(stats.router)

# Dev-only routers — only mounted when ENVIRONMENT=development
if settings.environment == "development":
    from dashboard_backend.routers import seed

    app.include_router(seed.router, prefix="/dev")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
