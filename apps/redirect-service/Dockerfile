ARG BASE_REGISTRY
FROM ${BASE_REGISTRY}/snip-base/python-base:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY packages/db/ packages/db/
COPY packages/queue/ packages/queue/
COPY packages/logger/ packages/logger/

COPY apps/redirect-service/ apps/redirect-service/

RUN cd apps/redirect-service && uv sync --frozen --no-dev

COPY apps/redirect-service/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_FROZEN=1
RUN adduser --system --no-create-home --group appuser
USER appuser

CMD ["/app/entrypoint.sh"]
