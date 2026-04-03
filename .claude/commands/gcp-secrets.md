---
name: gcp-secrets
description: Create, rotate, and list secrets and variables in GCP Secret Manager for the Snip project
---

# GCP Secrets Management

## Project Config

- **GCP Project**: `snip-491719`
- **Auth**: Application Default Credentials (`gcloud auth application-default login`)

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Environment-specific | `snip-{name}-{env}` | `snip-clerk-secret-pre-prod` |
| Global (shared across envs) | `snip-{name}` | `snip-cloudflare-api-token` |

Current environments: `pre-prod`

## Current Secrets

| Secret Name | Type | Consumed By |
|-------------|------|-------------|
| `snip-database-url-{env}` | env | Cloud Run backend (runtime) |
| `snip-clerk-publishable-{env}` | env | Cloud Run backend (runtime) + frontend Docker build |
| `snip-clerk-secret-{env}` | env | Cloud Run backend (runtime) |
| `snip-resend-api-key-{env}` | env | Cloud Run backend (runtime) |
| `snip-cloudflare-api-token` | global | Terraform CI (Cloudflare provider) |

## Architecture

Terraform creates and owns the secret **containers** and **IAM bindings**. Secret **values** are always set externally via `gcloud`. Cloud Run references secrets using `secret_key_ref` with `version = "latest"`, so new values are picked up on the next container start without Terraform changes.

**Flow:** Terraform (container + IAM) → `gcloud` (value) → Cloud Run (reads at startup via env var)

## Commands

### List all Snip secrets
```bash
gcloud secrets list --project=snip-491719 --filter="name:snip-"
```

### Read a secret value
```bash
gcloud secrets versions access latest \
  --secret=snip-clerk-publishable-pre-prod \
  --project=snip-491719
```

### Rotate a secret value
```bash
# Adding a new version automatically becomes the latest
echo -n "NEW_VALUE" | gcloud secrets versions add snip-{name}-{env} \
  --data-file=- \
  --project=snip-491719

# Cloud Run picks it up on next deploy (or restart)
# No Terraform changes needed — Terraform never manages values
```

### List versions of a secret
```bash
gcloud secrets versions list snip-{name}-{env} --project=snip-491719
```

### Disable an old version after rotation
```bash
gcloud secrets versions disable {version-number} \
  --secret=snip-{name}-{env} \
  --project=snip-491719
```

## Adding a New Secret End-to-End

All secret containers are created by Terraform, not `gcloud`. Follow these steps:

### 1. Register the container in Terraform

Add the secret name to `terraform/modules/secrets/main.tf`:
- **Env-specific:** add `"snip-{name}-${var.environment}"` to `local.env_secret_names`
- **Global:** add `"snip-{name}"` to `local.global_secret_names`

This creates the Secret Manager container and grants `secretAccessor` to the Cloud Run SA automatically (for env secrets).

### 2. Export the secret ID from the secrets module

Add an output in `terraform/modules/secrets/outputs.tf`:
```terraform
output "{name}_secret_id" {
  value = google_secret_manager_secret.secrets["snip-{name}-${var.environment}"].secret_id
}
```

### 3. Wire it into the Cloud Run module

**a)** Add a variable in `terraform/modules/cloud-run/variables.tf`:
```terraform
variable "{name}_secret_id" {
  description = "Secret Manager secret ID for {ENV_VAR_NAME}"
  type        = string
}
```

**b)** Add an `env` block in `terraform/modules/cloud-run/main.tf` inside `containers {}`:
```terraform
env {
  name = "{ENV_VAR_NAME}"
  value_source {
    secret_key_ref {
      secret  = var.{name}_secret_id
      version = "latest"
    }
  }
}
```

### 4. Pass the secret ID through terragrunt

In each `terraform/environments/{env}/cloud-run/terragrunt.hcl`, add:
```hcl
{name}_secret_id = dependency.secrets.outputs.{name}_secret_id
```

### 5. Apply Terraform and set the value

```bash
# Apply to create the container and IAM bindings
cd terraform/environments/{env}/secrets && terragrunt apply
cd terraform/environments/{env}/cloud-run && terragrunt apply

# Set the initial value via gcloud
echo -n "VALUE" | gcloud secrets versions add snip-{name}-{env} \
  --data-file=- \
  --project=snip-491719
```

### 6. Add the setting to the backend app

Add the field to `apps/dashboard-backend/src/dashboard_backend/config.py`:
```python
class Settings(BaseSettings):
    {name}: str = ""  # loaded from {ENV_VAR_NAME} env var
```

Pydantic `BaseSettings` auto-reads matching env vars (case-insensitive). In local dev, set it in `.env`.

## Adding a Plain (Non-Secret) Environment Variable

For config that isn't sensitive (no Secret Manager needed):

1. Add a `variable` in `terraform/modules/cloud-run/variables.tf` with a default
2. Add a plain `env { name = "..." value = var.{name} }` block in `cloud-run/main.tf`
3. Pass the value in `terragrunt.hcl` inputs (or rely on the default)
4. Add the field to `config.py`

## Important Rules

- **Terraform creates secret containers** — never create them via `gcloud secrets create`
- **Never set secret values via Terraform** — Terraform only manages containers and IAM
- **Never commit secret values** — use `echo -n` piped to `gcloud`, never write to a file first
- **Global secrets have no env suffix** — they are shared and rotated once for all environments
- **Rotation is zero-touch for Cloud Run** — new versions are picked up on next container start
