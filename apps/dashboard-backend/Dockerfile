FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace root files (needed for uv workspace resolution)
COPY pyproject.toml uv.lock ./

# Copy all workspace packages
COPY packages/db/ packages/db/
COPY packages/email/ packages/email/
COPY packages/auth/ packages/auth/

# Copy the app
COPY apps/dashboard-backend/ apps/dashboard-backend/

# Install production dependencies only
RUN cd apps/dashboard-backend && uv sync --frozen --no-dev

# Run with uvicorn
CMD ["uv", "run", "--no-sync", "--directory", "apps/dashboard-backend", \
     "uvicorn", "dashboard_backend.main:app", \
     "--host", "0.0.0.0", "--port", "8080"]
