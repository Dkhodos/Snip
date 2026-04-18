# ──────────────────────────────────────────────────────────────
#  snip-logger Makefile
#
#  All commands use `uv` for dependency management.
#  The workspace venv lives at the monorepo root (../../.venv).
# ──────────────────────────────────────────────────────────────

SHELL        := /bin/bash
ROOT         := $(shell git rev-parse --show-toplevel)
VENV         := $(ROOT)/.venv
UV           := uv
RUFF         := $(UV) run --package snip-logger ruff
PYRIGHT      := $(UV) run --package snip-logger pyright

# Sentinel file to track when deps were last synced
SYNC_STAMP   := $(VENV)/.snip-logger-synced

# Source files for change detection
SRC          := src/snip_logger

# ──────────────────────────────────────────────────────────────
#  Phony targets
# ──────────────────────────────────────────────────────────────

.PHONY: help venv install sync lint lint\:fix type\:check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_:\\]+:.*?## ' $(MAKEFILE_LIST) | \
		sed 's/\\:/:/g' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────────────────────
#  Environment
# ──────────────────────────────────────────────────────────────

venv: $(VENV)/bin/python ## Create the workspace venv (if missing)

$(VENV)/bin/python:
	$(UV) venv $(VENV)

install: venv ## Install all deps (including dev)
	$(UV) sync --all-packages --group dev
	@touch $(SYNC_STAMP)

# Auto-sync when pyproject.toml or lockfile changes
$(SYNC_STAMP): pyproject.toml $(ROOT)/uv.lock | $(VENV)/bin/python
	$(UV) sync --all-packages --group dev
	@touch $(SYNC_STAMP)

sync: $(SYNC_STAMP) ## Ensure deps are up-to-date (fast no-op if nothing changed)

# ──────────────────────────────────────────────────────────────
#  Lint
# ──────────────────────────────────────────────────────────────

lint: sync ## Run ruff linter + formatter check + type check
	$(RUFF) check $(SRC)
	$(RUFF) format --check $(SRC)
	$(PYRIGHT) $(SRC)

lint\:fix: sync ## Auto-fix lint issues and format
	$(RUFF) check --fix $(SRC)
	$(RUFF) format $(SRC)

type\:check: sync ## Run pyright type checking
	$(PYRIGHT) $(SRC)

# ──────────────────────────────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────────────────────────────

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage dist build
	rm -f $(SYNC_STAMP)
