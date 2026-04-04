---
name: gcp-secrets
description: Manage configuration values and secrets in GCP Parameter Manager + Secret Manager for the Snip project
---

# GCP Configuration & Secrets Management

## Project Config

- **GCP Project**: `snip-491719`
- **Auth**: Application Default Credentials (`gcloud auth application-default login`)

## Architecture

Git (`.devops/`) is the single source of truth for **what** exists. GCP holds the **live values**.

```
.devops/values/*.yaml  ──→  Terraform reads & merges  ──→  Parameter Manager (observable catalog)
                                     │
                                     ├──→  Cloud Run env_vars (plain values)
                                     └──→  Cloud Run secret_key_ref (secrets from SM)

.devops/secrets/*.yaml ──→  Terraform creates SM shells ──→  Values set manually via gcloud
```

| Layer | Owner | Where |
|---|---|---|
| Plain config values | Git (`.devops/values/`) | Repo |
| Secret key declarations | Git (`.devops/secrets/`) | Repo |
| Merged config upload | Terraform | Parameter Manager |
| Secret shell creation | Terraform | Secret Manager |
| Secret values | Manual / restricted CI | Secret Manager only |
| Service runtime config | Terraform | Cloud Run env vars |

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| PM parameter (per service) | `snip-{service}-config-{env}` | `snip-backend-config-pre-prod` |
| SM secret (env-specific) | `snip-{name}-{env}` | `snip-clerk-secret-pre-prod` |
| SM secret (global) | `snip-{name}` | `snip-cloudflare-api-token` |

Current environments: `pre-prod`

## Current Configuration

### Plain Values (Parameter Manager via `.devops/values/`)

| Key | Service(s) | Example Value |
|-----|-----------|---------------|
| `email_from` | all (global default) | `Snip <noreply@snip.dev>` |
| `environment` | all (env global) | `staging` |
| `gcp_project_id` | all (env global) | `snip-491719` |
| `email_provider` | backend | `resend` |
| `click_threshold` | backend | `100` |
| `allowed_origins` | backend | `https://app.pre-prod.snip-app.win,...` |
| `clerk_publishable_key` | backend, frontend | `pk_test_...` |
| `redirect_base_url` | frontend | `https://r.pre-prod.snip-app.win` |
| `queue_provider` | redirect | `gcp_pubsub` |
| `click_topic` | redirect | `click-events-pre-prod` |
| `analytics_provider` | click-worker | `gcp_bigquery` |
| `bq_dataset` | click-worker | `snip_analytics_pre_prod` |
| `bq_table` | click-worker | `click_events` |

### Secrets (Secret Manager — values never in Git)

| Secret Name | Consumed By |
|-------------|-------------|
| `snip-database-url-{env}` | backend, redirect, migrate |
| `snip-clerk-secret-{env}` | backend |
| `snip-resend-api-key-{env}` | backend |
| `snip-cloudflare-api-token` | Terraform CI (global) |

## YAML Hierarchy

```
.devops/values/global.yaml                          ← base defaults
.devops/values/{env}/global.yaml                    ← env overrides
.devops/values/{env}/{service}/values.yaml          ← service-specific
```

Merge order: global < env global < service (later values win).

## Commands

### Parameter Manager

```bash
# List all Snip parameters
gcloud parameter-manager parameters list --location=global --project=snip-491719

# Read a parameter's merged config (raw JSON, includes __REF__ placeholders)
gcloud parameter-manager parameters versions access current \
  --parameter=snip-backend-config-pre-prod \
  --location=global \
  --format='value(payload.data)' | base64 -d | jq .

# Render a parameter (resolves __REF__ secret references to actual values)
gcloud parameter-manager parameters versions render current \
  --parameter=snip-backend-config-pre-prod \
  --location=global
```

### Secret Manager

```bash
# List all Snip secrets
gcloud secrets list --project=snip-491719 --filter="name:snip-"

# Read a secret value
gcloud secrets versions access latest \
  --secret=snip-clerk-secret-pre-prod \
  --project=snip-491719

# Rotate a secret value (new version becomes latest automatically)
echo -n "NEW_VALUE" | gcloud secrets versions add snip-{name}-{env} \
  --data-file=- \
  --project=snip-491719

# Cloud Run picks up new secrets on next deploy/restart — no Terraform changes needed
```

## Adding a New Plain Config Value

1. Add the key to the appropriate YAML file in `.devops/values/{env}/{service}/values.yaml`
2. Run `terragrunt apply` on the `config` module — updates PM parameter and Cloud Run env vars
3. Add the field to the app's `config.py` (Pydantic auto-reads matching env vars)
4. For local dev, add to `.env`

## Adding a New Secret

1. Declare the secret in `.devops/secrets/{env}/{service}/secrets.yaml`:
   ```yaml
   secrets:
     - key: my_new_secret
       env_var: MY_NEW_SECRET
       secret_name: snip-my-new-secret
   ```
2. Run `terragrunt apply` on `secrets` module — creates the SM container and IAM
3. Run `terragrunt apply` on `config` module — updates PM parameter and Cloud Run secret_key_ref
4. Set the value via gcloud:
   ```bash
   echo -n "VALUE" | gcloud secrets versions add snip-my-new-secret-{env} \
     --data-file=- --project=snip-491719
   ```
5. Add the field to `config.py` and `.env`

## Important Rules

- **Terraform creates secret containers** — never create them via `gcloud secrets create`
- **Never set secret values via Terraform** — Terraform only manages containers and IAM
- **Never commit secret values** — use `echo -n` piped to `gcloud`
- **Plain values go in `.devops/values/`** — not in Secret Manager
- **Global secrets have no env suffix** — shared across environments
- **Rotation is zero-touch for Cloud Run** — new versions picked up on next container start
