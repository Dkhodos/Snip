ARG BASE_REGISTRY
FROM ${BASE_REGISTRY}/snip-base/python-base:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages/db/ packages/db/

RUN cd packages/db && uv sync --frozen --no-dev

CMD ["uv", "run", "--no-sync", "--directory", "packages/db", "alembic", "upgrade", "head"]
