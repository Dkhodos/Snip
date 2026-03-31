# ──────────────────────────────────────────────────────────────
#  dashboard-frontend Makefile
#
#  All commands use `pnpm` for dependency management.
# ──────────────────────────────────────────────────────────────

SHELL        := /bin/bash
PNPM         := pnpm

# Sentinel file to track when deps were last installed
SYNC_STAMP   := node_modules/.dashboard-frontend-synced

# Source files for change detection
SRC          := src

# ──────────────────────────────────────────────────────────────
#  Phony targets
# ──────────────────────────────────────────────────────────────

.PHONY: help install sync lint lint\:fix type-check test build clean

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
