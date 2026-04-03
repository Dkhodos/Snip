#!/usr/bin/env bash
set -euo pipefail

cd /app/apps/redirect-service

# Run migrations (shared DB)
uv run alembic -c ../../packages/db/alembic.ini upgrade head

# Start server
exec uv run uvicorn redirect_service.main:app --host 0.0.0.0 --port 8080
