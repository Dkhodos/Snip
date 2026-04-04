---
name: values
description: Manage plain config values in .devops/ YAML and GCP Parameter Manager (list, create, update, delete)
---

# Config Values Operations

Plain values live in `.devops/values/` YAML files. Terraform merges them and uploads to Parameter Manager + wires as Cloud Run env vars.

Merge order: `global.yaml` < `{env}/global.yaml` < `{env}/{service}/values.yaml` (later wins).

## List

```bash
gcloud parametermanager parameters versions describe current \
  --parameter=snip-backend-config-pre-prod \
  --location=global \
  --format='value(payload.data)' | base64 -d | jq .
```

## Create

1. Add key to `.devops/values/{env}/{service}/values.yaml`:
   ```yaml
   my_new_setting: "some-value"
   ```
2. Apply: `cd terraform/environments/{env}/config && terragrunt apply`
3. Key becomes `MY_NEW_SETTING` env var on Cloud Run (auto-uppercased)
4. Add field to app's `config.py` and `.env`

## Update

1. Edit the value in the YAML file
2. Apply: `cd terraform/environments/{env}/config && terragrunt apply`

## Delete

1. Remove the key from the YAML file
2. Apply: `cd terraform/environments/{env}/config && terragrunt apply`
3. Env var removed from Cloud Run on next service apply

## File locations

| Scope | Path |
|-------|------|
| All envs/services | `.devops/values/global.yaml` |
| All services in env | `.devops/values/{env}/global.yaml` |
| One service | `.devops/values/{env}/{service}/values.yaml` |
