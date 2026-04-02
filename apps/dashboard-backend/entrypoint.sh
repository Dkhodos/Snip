#!/bin/bash
set -e

echo "Running Alembic migrations..."
cd /app/packages/db
uv run --no-sync alembic upgrade head
echo "Migrations complete."
cd /app

echo "Starting uvicorn..."
exec uv run --no-sync --directory apps/dashboard-backend \
  uvicorn dashboard_backend.main:app --host 0.0.0.0 --port 8080
