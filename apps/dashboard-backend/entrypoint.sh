#!/bin/bash
set -e

# Migrations are managed by the CI pipeline (migrate.yml → snip-migrate Cloud Run Job).
# This service starts directly without running migrations.

echo "Starting dashboard-backend..."
exec uv run --no-sync --directory apps/dashboard-backend dashboard-serve
