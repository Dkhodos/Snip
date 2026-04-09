---
name: lint-all
description: Lint all projects affected by current changes
---

# Lint All Affected Projects

Determine which projects have changes and lint them.

## Instructions

1. Run `git diff --name-only HEAD` (or `git diff --name-only` for unstaged) to find changed files.

2. Map changed files to projects:
   - `apps/dashboard-backend/**` -> `make dashboard-backend:lint`
   - `apps/dashboard-frontend/**` -> `cd apps/dashboard-frontend && npx biome check .`
   - `apps/redirect-service/**` -> `make redirect-service:lint`
   - `apps/click-worker/**` -> `make click-worker:lint`
   - `packages/db/**` -> `make db:lint`
   - `packages/auth/**` -> `make auth:lint`
   - `packages/email/**` -> `make email:lint`
   - `packages/logger/**` -> `make logger:lint`
   - `packages/queue/**` -> `make queue:lint`
   - `packages/analytics/**` -> `make analytics:lint`
   - `packages/storage/**` -> `make storage:lint`
   - `packages/og-image/**` -> `make og-image:lint`

3. Run all affected lint commands in parallel where possible.

4. Report results: which projects passed, which failed, and specific errors.

If no changes detected, lint all projects.
