FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY packages/queue/ packages/queue/
COPY packages/analytics/ packages/analytics/
COPY packages/logger/ packages/logger/

COPY apps/click-worker/ apps/click-worker/

RUN cd apps/click-worker && uv sync --frozen --no-dev

COPY apps/click-worker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_FROZEN=1
RUN adduser --system --no-create-home --group appuser
USER appuser

CMD ["/app/entrypoint.sh"]
