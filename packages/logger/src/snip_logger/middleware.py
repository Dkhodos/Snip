"""FastAPI HTTP logging middleware."""

import time
import uuid

import structlog
from fastapi import Request, Response


async def logging_middleware(request: Request, call_next) -> Response:  # type: ignore[type-arg]
    """Log every HTTP request with method, path, status, duration, and request_id.

    Register with: ``app.middleware("http")(logging_middleware)``

    Log levels:
    - 2xx / 3xx → info
    - 4xx        → warning
    - 5xx        → error
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=str(uuid.uuid4()))

    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    status = response.status_code
    log = structlog.get_logger()
    if status >= 500:
        log_fn = log.error
    elif status >= 400:
        log_fn = log.warning
    else:
        log_fn = log.info

    log_fn(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=status,
        duration_ms=duration_ms,
    )

    structlog.contextvars.clear_contextvars()
    return response
