#!/usr/bin/env bash
set -euo pipefail

# Migrations are handled by dashboard-backend — redirect-service only reads.

echo "Starting uvicorn..."
exec uv run --no-sync --directory /app/apps/redirect-service \
  uvicorn redirect_service.main:app --host 0.0.0.0 --port 8080
