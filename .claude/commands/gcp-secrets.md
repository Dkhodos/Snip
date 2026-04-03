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

### Create a new env-specific secret
```bash
# 1. Create the container
gcloud secrets create snip-{name}-{env} \
  --replication-policy=automatic \
  --project=snip-491719

# 2. Set the initial value
echo -n "VALUE" | gcloud secrets versions add snip-{name}-{env} \
  --data-file=- \
  --project=snip-491719

# 3. Register it in Terraform so the container and IAM are managed
# Add "snip-{name}-{env}" to local.env_secret_names in:
#   terraform/modules/secrets/main.tf
```

### Create a new global secret
```bash
# 1. Create the container
gcloud secrets create snip-{name} \
  --replication-policy=automatic \
  --project=snip-491719

# 2. Set the initial value
echo -n "VALUE" | gcloud secrets versions add snip-{name} \
  --data-file=- \
  --project=snip-491719

# 3. Register it in Terraform
# Add "snip-{name}" to local.global_secret_names in:
#   terraform/modules/secrets/main.tf
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

1. **Create and populate in GCP** (commands above)
2. **Register container in Terraform** — add the name to `local.env_secret_names` or `local.global_secret_names` in `terraform/modules/secrets/main.tf`
3. **Grant access if needed** — Cloud Run SA access is automatic for all env secrets. For CI workflows, add a `get-secretmanager-secrets` step referencing `projects/snip-491719/secrets/{name}/versions/latest`
4. **Reference in Cloud Run** — add a `secret_env_var` or mount in `terraform/modules/cloud-run/main.tf`

## Important Rules

- **Never set secret values via Terraform** — Terraform only manages containers and IAM
- **Never commit secret values** — use `echo -n` piped to `gcloud`, never write to a file first
- **Global secrets have no env suffix** — they are shared and rotated once for all environments
- **Rotation is zero-touch for Cloud Run** — new versions are picked up on next container start
