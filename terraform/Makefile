# ──────────────────────────────────────────────────────────────
#  snip-terraform Makefile
#
#  Wraps Terragrunt / Checkov commands for local and CI use.
#  Uses `uv` for managing Checkov as a Python dependency.
# ──────────────────────────────────────────────────────────────

SHELL        := /bin/bash
ROOT         := $(shell git rev-parse --show-toplevel)
VENV         := $(ROOT)/.venv
UV           := uv
CHECKOV      := $(UV) run --package snip-terraform checkov

# Sentinel file to track when deps were last synced
SYNC_STAMP   := $(VENV)/.snip-terraform-synced

# Default environment for local work
ENVIRONMENT  ?= pre-prod
WORKING_DIR  := environments/$(ENVIRONMENT)

# ──────────────────────────────────────────────────────────────
#  Phony targets
# ──────────────────────────────────────────────────────────────

.PHONY: help venv install sync check plan plan\:local apply apply\:local init init\:local clean

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

$(SYNC_STAMP): pyproject.toml $(ROOT)/uv.lock | $(VENV)/bin/python
	$(UV) sync --all-packages --group dev
	@touch $(SYNC_STAMP)

sync: $(SYNC_STAMP) ## Ensure deps are up-to-date (fast no-op if nothing changed)

# ──────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────

# Load .env into the environment for :local targets
define load_env
	set -a && source .env && set +a
endef

# ──────────────────────────────────────────────────────────────
#  Checkov
# ──────────────────────────────────────────────────────────────

check: sync ## Run Checkov security scan
	$(CHECKOV) \
		--config-file .checkov.yml \
		--directory . \
		--framework terraform \
		--output cli \
		--output github_failed_only \
		--soft-fail-on LOW \
		--compact

# ──────────────────────────────────────────────────────────────
#  Terragrunt — CI (expects env vars already set)
# ──────────────────────────────────────────────────────────────

init: ## Terragrunt init (CI — env vars must be set)
	cd $(WORKING_DIR) && terragrunt init --all --non-interactive

plan: init ## Terragrunt plan (CI — env vars must be set)
	cd $(WORKING_DIR) && terragrunt plan --all --non-interactive -no-color

apply: init ## Terragrunt apply (CI — env vars must be set)
	cd $(WORKING_DIR) && terragrunt apply --all --non-interactive -auto-approve

# ──────────────────────────────────────────────────────────────
#  Terragrunt — Local (sources .env for credentials)
# ──────────────────────────────────────────────────────────────

init\:local: ## Terragrunt init (local — sources .env)
	$(load_env) && cd $(WORKING_DIR) && terragrunt init --all --non-interactive

plan\:local: init\:local ## Terragrunt plan (local — sources .env)
	$(load_env) && cd $(WORKING_DIR) && terragrunt plan --all --non-interactive

apply\:local: init\:local ## Terragrunt apply (local — sources .env)
	$(load_env) && cd $(WORKING_DIR) && terragrunt apply --all --non-interactive -auto-approve

# ──────────────────────────────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────────────────────────────

clean: ## Remove caches and build artifacts
	find . -type d -name .terragrunt-cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .terraform -exec rm -rf {} + 2>/dev/null || true
	rm -f $(SYNC_STAMP)
