FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY packages/db/ packages/db/
COPY packages/queue/ packages/queue/
COPY packages/logger/ packages/logger/

COPY apps/redirect-service/ apps/redirect-service/

RUN cd apps/redirect-service && uv sync --frozen --no-dev

COPY apps/redirect-service/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
