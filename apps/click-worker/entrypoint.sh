#!/usr/bin/env bash
set -euo pipefail

cd /app/apps/click-worker

exec uv run --no-sync uvicorn click_worker.main:app --host 0.0.0.0 --port 8080
