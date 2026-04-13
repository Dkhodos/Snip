SHELL := /bin/bash

.PHONY: help generate validate check install

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install pkl CLI
	@command -v pkl > /dev/null && echo "pkl already installed: $$(pkl --version)" || { echo "Installing pkl..."; brew install pkl; }

generate: ## Generate YAML from PKL sources
	@./scripts/generate.sh

validate: ## Validate all PKL files without generating
	@command -v pkl > /dev/null || { echo "ERROR: pkl not installed. Run: make devops:install"; exit 1; }
	@errors=0; \
	for f in $$(find pkl -name "*.pkl" ! -path "*/schemas/*" | sort); do \
		if pkl eval "$$f" > /dev/null 2>&1; then \
			echo "  ok  $$f"; \
		else \
			echo "FAIL  $$f"; \
			pkl eval "$$f" 2>&1 | head -5; \
			errors=$$((errors + 1)); \
		fi; \
	done; \
	if [ "$$errors" -gt 0 ]; then echo ""; echo "FAILED: $$errors file(s) invalid."; exit 1; fi; \
	echo ""; echo "All PKL files valid."

check: generate ## Generate and verify no drift from committed YAML
	@if ! git diff --quiet -- values/ secrets/ services/; then \
		echo ""; \
		echo "ERROR: Generated YAML is out of sync with PKL sources."; \
		echo "Run 'make devops:generate' and commit the results."; \
		echo ""; \
		git diff --stat -- values/ secrets/ services/; \
		exit 1; \
	fi
	@echo "Generated YAML is in sync."
