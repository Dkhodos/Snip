# ──────────────────────────────────────────────────────────────
#  dashboard-backend Makefile
#
#  All commands use `uv` for dependency management.
#  The workspace venv lives at the monorepo root (../../.venv).
# ──────────────────────────────────────────────────────────────

SHELL        := /bin/bash
ROOT         := $(shell git rev-parse --show-toplevel)
VENV         := $(ROOT)/.venv
UV           := uv
PYTHON       := $(UV) run --package dashboard-backend python
PYTEST       := $(UV) run --package dashboard-backend pytest
RUFF         := $(UV) run --package dashboard-backend ruff
PYRIGHT      := $(UV) run --package dashboard-backend pyright

# Sentinel file to track when deps were last synced
SYNC_STAMP   := $(VENV)/.dashboard-backend-synced

# Source files for change detection
SRC          := src/dashboard_backend
TESTS        := tests

# ──────────────────────────────────────────────────────────────
#  Phony targets
# ──────────────────────────────────────────────────────────────

.PHONY: help venv install sync lint lint\:fix type\:check test\:unit clean build-image deploy

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
	$(UV) sync --all-packages --extra dev
	@touch $(SYNC_STAMP)

# Auto-sync when pyproject.toml or lockfile changes
$(SYNC_STAMP): pyproject.toml $(ROOT)/uv.lock | $(VENV)/bin/python
	$(UV) sync --all-packages --extra dev
	@touch $(SYNC_STAMP)

sync: $(SYNC_STAMP) ## Ensure deps are up-to-date (fast no-op if nothing changed)

# ──────────────────────────────────────────────────────────────
#  Lint
# ──────────────────────────────────────────────────────────────

lint: sync ## Run ruff linter + formatter check + type check
	$(RUFF) check $(SRC) $(TESTS)
	$(RUFF) format --check $(SRC) $(TESTS)
	$(PYRIGHT) $(SRC)

lint\:fix: sync ## Auto-fix lint issues and format
	$(RUFF) check --fix $(SRC) $(TESTS)
	$(RUFF) format $(SRC) $(TESTS)

type\:check: sync ## Run pyright type checking
	$(PYRIGHT) $(SRC)

# ──────────────────────────────────────────────────────────────
#  Test
# ──────────────────────────────────────────────────────────────

test\:unit: sync ## Run unit tests with coverage report
	$(PYTEST) $(TESTS) \
		--cov=$(SRC) \
		--cov-report=term-missing \
		--cov-fail-under=90 \
		-v

# ──────────────────────────────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────────────────────────────

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage dist build
	rm -f $(SYNC_STAMP)

# ──────────────────────────────────────────────────────────────
#  Docker / Cloud Run
#
#  Required variables (pass on command line or export to env):
#    IMAGE    — full image ref, e.g. us-docker.pkg.dev/project/repo/dashboard-backend:sha
#    SERVICE  — Cloud Run service name, e.g. snip-backend-pre-prod
#    REGION   — GCP region, e.g. europe-west1
# ──────────────────────────────────────────────────────────────

build-image: ## Build and push Docker image (requires IMAGE)
	docker build \
		-t "$(IMAGE)" \
		-f apps/dashboard-backend/Dockerfile \
		$(ROOT)
	docker push "$(IMAGE)"

deploy: ## Deploy image to Cloud Run (requires IMAGE, SERVICE, REGION)
	gcloud run deploy $(SERVICE) \
		--image "$(IMAGE)" \
		--region $(REGION) \
		--quiet
