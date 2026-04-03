FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages/db/ packages/db/

RUN cd packages/db && uv sync --frozen --no-dev

CMD ["uv", "run", "--no-sync", "--directory", "packages/db", "alembic", "upgrade", "head"]
