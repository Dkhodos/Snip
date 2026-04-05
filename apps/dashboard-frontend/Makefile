# ──────────────────────────────────────────────────────────────
#  dashboard-frontend Makefile
#
#  All commands use `pnpm` for dependency management.
# ──────────────────────────────────────────────────────────────

SHELL        := /bin/bash
ROOT         := $(shell git rev-parse --show-toplevel)
PNPM         := pnpm

# Sentinel file to track when deps were last installed
SYNC_STAMP   := node_modules/.dashboard-frontend-synced

# Source files for change detection
SRC          := src

# ──────────────────────────────────────────────────────────────
#  Phony targets
# ──────────────────────────────────────────────────────────────

.PHONY: help install sync lint lint\:fix type-check test build clean build-image deploy

help: ## Show this help
	@grep -E '^[a-zA-Z_:\\-]+:.*?## ' $(MAKEFILE_LIST) | \
		sed 's/\\:/:/g' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────────────────────
#  Environment
# ──────────────────────────────────────────────────────────────

install: ## Install all deps
	$(PNPM) install
	@touch $(SYNC_STAMP)

# Auto-sync when package.json or lockfile changes
$(SYNC_STAMP): package.json pnpm-lock.yaml
	$(PNPM) install
	@touch $(SYNC_STAMP)

sync: $(SYNC_STAMP) ## Ensure deps are up-to-date (fast no-op if nothing changed)

# ──────────────────────────────────────────────────────────────
#  Lint
# ──────────────────────────────────────────────────────────────

lint: sync ## Run biome linter + formatter check
	$(PNPM) exec biome check .

lint\:fix: sync ## Auto-fix lint issues and format
	$(PNPM) exec biome check --write .

# ──────────────────────────────────────────────────────────────
#  Type-check
# ──────────────────────────────────────────────────────────────

type-check: sync ## Run TypeScript type checking
	$(PNPM) exec tsc --noEmit

# ──────────────────────────────────────────────────────────────
#  Test
# ──────────────────────────────────────────────────────────────

test: sync ## Run unit tests
	$(PNPM) exec vitest run

# ──────────────────────────────────────────────────────────────
#  Build
# ──────────────────────────────────────────────────────────────

build: sync ## Build for production
	$(PNPM) exec tsc -b
	$(PNPM) exec vite build

# ──────────────────────────────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────────────────────────────

clean: ## Remove caches and build artifacts
	rm -rf dist node_modules/.vite
	rm -f $(SYNC_STAMP)

# ──────────────────────────────────────────────────────────────
#  Docker / Cloud Run
#
#  Required variables (pass on command line or export to env):
#    IMAGE    — full image ref, e.g. us-docker.pkg.dev/project/repo/dashboard-frontend:sha
#    SERVICE  — Cloud Run service name, e.g. snip-frontend-pre-prod
#    REGION   — GCP region, e.g. europe-west1
#
#  Build-time (baked into the Vite bundle):
#    VITE_CLERK_PUBLISHABLE_KEY
#    VITE_API_URL
#    VITE_REDIRECT_BASE_URL
#
#  Deploy-time (runtime env var for nginx reverse proxy):
#    BACKEND_URL — backend Cloud Run service URL
# ──────────────────────────────────────────────────────────────

build-image: ## Build and push Docker image (requires IMAGE, BASE_REGISTRY; optionally VITE_CLERK_PUBLISHABLE_KEY, VITE_API_URL, VITE_REDIRECT_BASE_URL)
	docker build \
		--build-arg BASE_REGISTRY="$(BASE_REGISTRY)" \
		--build-arg VITE_CLERK_PUBLISHABLE_KEY="$(VITE_CLERK_PUBLISHABLE_KEY)" \
		--build-arg VITE_API_URL="$(VITE_API_URL)" \
		--build-arg VITE_REDIRECT_BASE_URL="$(VITE_REDIRECT_BASE_URL)" \
		-t "$(IMAGE)" \
		-f $(ROOT)/apps/dashboard-frontend/Dockerfile \
		$(ROOT)
	docker push "$(IMAGE)"

deploy: ## Deploy image to Cloud Run (requires IMAGE, SERVICE, REGION, BACKEND_URL)
	gcloud run deploy $(SERVICE) \
		--image "$(IMAGE)" \
		--region $(REGION) \
		--update-env-vars "BACKEND_URL=$(BACKEND_URL)" \
		--quiet
