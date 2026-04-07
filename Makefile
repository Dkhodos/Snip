# ──────────────────────────────────────────────────────────────
#  Snip monorepo root Makefile
#
#  Delegates to sub-project Makefiles via:
#    make <project>:<target>
#
#  Examples:
#    make dashboard-backend:lint
#    make dashboard-backend:test:unit
# ──────────────────────────────────────────────────────────────

SHELL := /bin/bash

# Map project names to their directories
PROJECTS := \
	dashboard-backend:apps/dashboard-backend \
	dashboard-frontend:apps/dashboard-frontend \
	redirect-service:apps/redirect-service \
	click-worker:apps/click-worker \
	db:packages/db \
	email:packages/email \
	auth:packages/auth \
	logger:packages/logger \
	queue:packages/queue \
	analytics:packages/analytics \
	storage:packages/storage \
	og-image:packages/og-image \
	e2e:apps/e2e \
	terraform:terraform

# Lookup helper: $(call project_dir,<name>) → directory path
project_dir = $(patsubst $(1):%,%,$(filter $(1):%,$(PROJECTS)))

.PHONY: help

help: ## Show this help
	@echo "Usage: make <project>:<target>"
	@echo ""
	@echo "Projects:"
	@$(foreach p,$(PROJECTS),echo "  $(firstword $(subst :, ,$(p)))";)
	@echo ""
	@echo "To see targets for a project:"
	@echo "  make <project>:help"

# ──────────────────────────────────────────────────────────────
#  Catch-all: split on first colon, delegate to sub-Makefile
# ──────────────────────────────────────────────────────────────

%:
	$(eval _proj := $(firstword $(subst :, ,$@)))
	$(eval _rest := $(patsubst $(_proj):%,%,$@))
	$(eval _dir  := $(call project_dir,$(_proj)))
	@if [ -z "$(_dir)" ]; then \
		echo "Unknown project: $(_proj)"; \
		echo "Run 'make help' for available projects."; \
		exit 1; \
	fi
	@if [ ! -f "$(_dir)/Makefile" ]; then \
		echo "No Makefile found in $(_dir)/"; \
		exit 1; \
	fi
	$(MAKE) -C $(_dir) $(subst :,\:,$(_rest))
