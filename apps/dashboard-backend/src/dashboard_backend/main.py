"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard_backend.config import settings
from snip_db.engine import create_engine, create_session_factory, init_session_factory

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
