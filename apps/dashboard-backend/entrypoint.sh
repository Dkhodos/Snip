#!/bin/bash
set -e

echo "Running Alembic migrations..."
cd /app
uv run --no-sync --directory packages/db \
  alembic -c packages/db/alembic.ini upgrade head
echo "Migrations complete."

echo "Starting uvicorn..."
exec uv run --no-sync --directory apps/dashboard-backend \
  uvicorn dashboard_backend.main:app --host 0.0.0.0 --port 8080
