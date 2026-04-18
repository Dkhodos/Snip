#!/usr/bin/env bash
set -euo pipefail

# Migrations are handled by dashboard-backend — redirect-service only reads.

echo "Starting redirect-service..."
exec uv run --no-sync --directory /app/apps/redirect-service redirect-serve
