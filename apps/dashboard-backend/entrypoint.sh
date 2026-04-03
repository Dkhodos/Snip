#!/bin/bash
set -e

# Migrations are managed by the CI pipeline (migrate.yml → snip-migrate Cloud Run Job).
# This service starts directly without running migrations.

echo "Starting uvicorn..."
exec uv run --no-sync --directory apps/dashboard-backend \
  uvicorn dashboard_backend.main:app --host 0.0.0.0 --port 8080
