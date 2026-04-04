---
name: secrets
description: Manage GCP Secret Manager secrets for Snip (list, create, update, delete)
---

# Secret Manager Operations

Secrets are declared in `.devops/secrets/{env}/{service}/secrets.yaml` and shells created by Terraform. Values are set manually via gcloud.

## List

```bash
gcloud secrets list --project=snip-491719 --filter="name:snip-"
```

## Create

1. Add to `.devops/secrets/{env}/{service}/secrets.yaml`:
   ```yaml
   secrets:
     - key: my_api_key
       env_var: MY_API_KEY
       secret_name: snip-my-api-key
   ```
2. Apply: `cd terraform/environments/{env}/config && terragrunt apply`
3. Set value:
   ```bash
   echo -n "VALUE" | gcloud secrets versions add snip-my-api-key-{env} --data-file=- --project=snip-491719
   ```
4. Add field to app's `config.py` and `.env`

## Update (rotate value)

```bash
echo -n "NEW_VALUE" | gcloud secrets versions add snip-clerk-secret-pre-prod --data-file=- --project=snip-491719
```

Cloud Run picks up new value on next deploy — no Terraform changes needed.

## Delete

1. Remove entry from `.devops/secrets/{env}/{service}/secrets.yaml`
2. Apply: `cd terraform/environments/{env}/config && terragrunt apply`
3. Terraform destroys the SM shell and IAM bindings

## Rules

- Terraform creates shells — never `gcloud secrets create`
- Never commit secret values — pipe with `echo -n`
- Global secrets (no env suffix) go in `.devops/secrets/global.yaml`
