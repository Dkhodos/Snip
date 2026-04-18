# ──────────────────────────────────────────────────────────────
#  Snip security Makefile
#
#  Thin wrappers around security scanners so local runs match CI.
#  Deps are declared in security/pyproject.toml and resolved via
#  the root uv workspace — no global installs needed.
# ──────────────────────────────────────────────────────────────

SHELL      := /bin/bash
ROOT       := $(shell git rev-parse --show-toplevel)
VENV       := $(ROOT)/.venv
UV         := uv
SKYLOS     := $(UV) run --package snip-security skylos
PIP_AUDIT  := $(UV) run --package snip-security pip-audit

# Sentinel file to track when deps were last synced
SYNC_STAMP := $(VENV)/.snip-security-synced

# Skylos confidence threshold (matches CI default)
CONFIDENCE ?= 60

# Python source roots to scan (mirrors bandit's list in .github/workflows/security.yml)
PY_SRC := \
	apps/dashboard-backend/src \
	apps/redirect-service/src \
	apps/click-worker/src \
	packages/analytics/src \
	packages/auth/src \
	packages/db/src \
	packages/email/src \
	packages/logger/src \
	packages/queue/src \
	packages/storage/src \
	packages/og-image/src

.PHONY: help venv install sync skylos\:scan skylos\:gate skylos pip-audit\:scan

help: ## Show this help
	@grep -E '^[a-zA-Z_:\\-]+:.*?## ' $(MAKEFILE_LIST) | \
		sed 's/\\:/:/g' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

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
#  Skylos — dead code detection
# ──────────────────────────────────────────────────────────────

skylos\:scan: sync ## Run Skylos dead-code scan (advisory, never fails)
	cd $(ROOT) && $(SKYLOS) --confidence $(CONFIDENCE) $(PY_SRC) || true

skylos\:gate: sync ## Run Skylos as a gate (exit 1 on findings above threshold)
	cd $(ROOT) && $(SKYLOS) --gate --confidence $(CONFIDENCE) $(PY_SRC)

skylos: skylos\:scan ## Alias for skylos:scan

# ──────────────────────────────────────────────────────────────
#  pip-audit — Python dependency CVE scan
# ──────────────────────────────────────────────────────────────

pip-audit\:scan: sync ## Run pip-audit against the workspace lockfile
	cd $(ROOT) && $(UV) export --no-hashes --all-packages --frozen \
		| grep -v '^-e ' \
		| grep -v '^[[:space:]]*#' \
		| grep -v '^#' \
		| grep -v '^$$' \
		> /tmp/requirements.txt
	$(PIP_AUDIT) -r /tmp/requirements.txt --desc || true
