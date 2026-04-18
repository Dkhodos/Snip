#!/usr/bin/env bash
set -euo pipefail

cd /app/apps/click-worker

exec uv run --no-sync worker-serve
