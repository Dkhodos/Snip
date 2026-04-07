# ──────────────────────────────────────────────────────────────
#  e2e Makefile
#
#  All commands use `pnpm` for dependency management.
# ──────────────────────────────────────────────────────────────

SHELL        := /bin/bash
ROOT         := $(shell git rev-parse --show-toplevel)
PNPM         := pnpm

# Sentinel file to track when deps were last installed
SYNC_STAMP   := node_modules/.e2e-synced

# ──────────────────────────────────────────────────────────────
#  Phony targets
# ──────────────────────────────────────────────────────────────

.PHONY: help install sync lint lint\:fix type-check test test\:e2e test\:system test\:setup clean

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

test: sync ## Run all Playwright tests
	$(PNPM) exec playwright test

test\:e2e: sync ## Run E2E tests only
	$(PNPM) exec playwright test --project=e2e

test\:system: sync ## Run system tests only
	$(PNPM) exec playwright test --project=system

test\:setup: sync ## Run auth setup only
	$(PNPM) exec playwright test --project=setup

# ──────────────────────────────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────────────────────────────

clean: ## Remove caches and build artifacts
	rm -rf playwright-report test-results
	rm -f $(SYNC_STAMP)
