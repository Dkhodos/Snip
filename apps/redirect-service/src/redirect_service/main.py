"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from snip_db.engine import create_engine, create_session_factory, init_session_factory
from snip_logger import configure_logging, logging_middleware
from snip_telemetry import init_telemetry

from redirect_service.config import settings
from redirect_service.exceptions import LinkExpiredError, LinkNotFoundError
from redirect_service.routers import redirect


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_telemetry(settings.build_telemetry_config())
    configure_logging(is_local=settings.environment == "development")
    engine = create_engine(settings.effective_database_url)
    session_factory = create_session_factory(engine)
    init_session_factory(session_factory)
    yield
    await engine.dispose()


app = FastAPI(title="Snip Redirect Service", version="0.1.0", lifespan=lifespan)

app.middleware("http")(logging_middleware)


@app.exception_handler(LinkNotFoundError)
async def link_not_found_handler(request: Request, exc: LinkNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(LinkExpiredError)
async def link_expired_handler(request: Request, exc: LinkExpiredError) -> JSONResponse:
    return JSONResponse(status_code=410, content={"detail": exc.detail})


app.include_router(redirect.router)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
