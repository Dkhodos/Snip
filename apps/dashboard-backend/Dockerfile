ARG BASE_REGISTRY
FROM ${BASE_REGISTRY}/snip-base/python-base:latest

WORKDIR /app

# Copy workspace root files (needed for uv workspace resolution)
COPY pyproject.toml uv.lock ./

# Copy all workspace packages
COPY packages/db/ packages/db/
COPY packages/email/ packages/email/
COPY packages/auth/ packages/auth/
COPY packages/logger/ packages/logger/

# Copy the app
COPY apps/dashboard-backend/ apps/dashboard-backend/

# Install production dependencies only
RUN cd apps/dashboard-backend && uv sync --frozen --no-dev

# Copy entrypoint script
COPY apps/dashboard-backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_FROZEN=1
RUN adduser --system --no-create-home --group appuser
USER appuser

CMD ["/app/entrypoint.sh"]

