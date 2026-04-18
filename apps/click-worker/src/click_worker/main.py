"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from snip_logger import configure_logging, logging_middleware
from snip_telemetry import init_telemetry

from click_worker.config import settings
from click_worker.routers import ingest


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_telemetry(settings.build_telemetry_config())
    configure_logging(is_local=settings.environment == "development")
    yield


app = FastAPI(title="Snip Click Worker", version="0.1.0", lifespan=lifespan)

app.middleware("http")(logging_middleware)

app.include_router(ingest.router)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
