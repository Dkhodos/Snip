# ---------------------------------------------------------------------------
# Config module — reads .devops/ YAML, pushes to Parameter Manager,
# creates Secret Manager shells, and outputs env var maps for Cloud Run.
# ---------------------------------------------------------------------------

# Enable Parameter Manager API (idempotent)
resource "google_project_service" "parametermanager" {
  count   = var.env_enabled ? 1 : 0
  service = "parametermanager.googleapis.com"

  disable_on_destroy = false
}

# ---------------------------------------------------------------------------
# 1. Read and merge YAML hierarchy per service
# ---------------------------------------------------------------------------

locals {
  # Base defaults — shared across all envs and services
  global_values = yamldecode(file("${var.devops_root}/values/global.yaml"))

  # Environment-level overrides
  env_values = yamldecode(file("${var.devops_root}/values/${var.environment}/global.yaml"))

  # Per-service values (merged on top of global + env)
  service_values = {
    for svc in var.services : svc => yamldecode(
      file("${var.devops_root}/values/${var.environment}/${svc}/values.yaml")
    )
  }

  # Final merged config per service — later values win
  merged_config = {
    for svc in var.services : svc => merge(
      local.global_values,
      local.env_values,
      local.service_values[svc],
    )
  }

  # ---------------------------------------------------------------------------
  # 2. Read secret declarations per service
  # ---------------------------------------------------------------------------

  # Global secrets (environment-independent)
  global_secrets_raw = yamldecode(file("${var.devops_root}/secrets/global.yaml"))
  global_secrets     = try(local.global_secrets_raw.secrets, [])

  # Per-service secrets — only if the file exists
  service_secrets_raw = {
    for svc in var.services : svc => (
      fileexists("${var.devops_root}/secrets/${var.environment}/${svc}/secrets.yaml")
      ? yamldecode(file("${var.devops_root}/secrets/${var.environment}/${svc}/secrets.yaml"))
      : { secrets = [] }
    )
  }

  service_secrets = {
    for svc in var.services : svc => try(local.service_secrets_raw[svc].secrets, [])
  }

  # Flatten all env-specific secrets into a unique set (by secret_name-{env})
  all_env_secret_names = toset(distinct(flatten([
    for svc in var.services : [
      for s in local.service_secrets[svc] : "${s.secret_name}-${var.environment}"
    ]
  ])))

  all_global_secret_names = toset([for s in local.global_secrets : s.secret_name])

  # ---------------------------------------------------------------------------
  # 3. Build output maps for Cloud Run consumption
  # ---------------------------------------------------------------------------

  # env_vars: service → { UPPER_KEY = "value", ... }
  env_vars = {
    for svc in var.services : svc => {
      for k, v in local.merged_config[svc] : upper(k) => tostring(v)
    }
  }

  # secret_env_vars: service → { ENV_VAR = "secret-id", ... }
  secret_env_vars = {
    for svc in var.services : svc => {
      for s in local.service_secrets[svc] : s.env_var => "${s.secret_name}-${var.environment}"
    }
  }

  # ---------------------------------------------------------------------------
  # 4. Build PM parameter data (JSON with __REF__ for secrets)
  # ---------------------------------------------------------------------------

  pm_parameter_data = {
    for svc in var.services : svc => merge(
      local.merged_config[svc],
      {
        for s in local.service_secrets[svc] : s.key => "__REF__(//secretmanager.googleapis.com/projects/${var.project_id}/secrets/${s.secret_name}-${var.environment}/versions/latest)"
      },
    )
  }

  # Cross-product of (service, secret) for PM → SM IAM bindings
  pm_secret_bindings = var.env_enabled && var.manage_secrets ? {
    for pair in flatten([
      for svc in var.services : [
        for s in local.service_secrets[svc] : {
          key         = "${svc}--${s.secret_name}-${var.environment}"
          service     = svc
          secret_name = "${s.secret_name}-${var.environment}"
        }
      ]
    ]) : pair.key => pair
  } : {}
}

# ---------------------------------------------------------------------------
# Secret Manager — only when manage_secrets = true (Phase 3b)
# When false, SM stays in the existing secrets/ module.
# ---------------------------------------------------------------------------

resource "google_secret_manager_secret" "env_secrets" {
  for_each  = var.manage_secrets ? local.all_env_secret_names : toset([])
  secret_id = each.key

  replication {
    auto {}
  }

  labels = {
    env     = var.environment
    managed = "config-module"
  }
}

resource "google_secret_manager_secret" "global_secrets" {
  for_each  = var.manage_secrets ? local.all_global_secret_names : toset([])
  secret_id = each.key

  replication {
    auto {}
  }

  labels = {
    managed = "config-module"
  }
}

resource "google_secret_manager_secret_iam_member" "cloud_run_access" {
  for_each = var.manage_secrets ? local.all_env_secret_names : toset([])

  secret_id = google_secret_manager_secret.env_secrets[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account_email}"
}

# ---------------------------------------------------------------------------
# Parameter Manager — one parameter per service (JSON blob)
# ---------------------------------------------------------------------------

resource "google_parameter_manager_parameter" "service_config" {
  for_each = var.env_enabled ? toset(var.services) : toset([])

  parameter_id = "snip-${each.key}-config-${var.environment}"
  format       = "JSON"

  labels = {
    env     = var.environment
    service = each.key
  }

  depends_on = [google_project_service.parametermanager]
}

resource "google_parameter_manager_parameter_version" "current" {
  for_each = var.env_enabled ? toset(var.services) : toset([])

  parameter            = google_parameter_manager_parameter.service_config[each.key].id
  parameter_version_id = "current"
  parameter_data       = jsonencode(local.pm_parameter_data[each.key])
}

# ---------------------------------------------------------------------------
# IAM: CI SA → parameterViewer (for frontend build reads from PM)
# ---------------------------------------------------------------------------

resource "google_project_iam_member" "ci_parameter_viewer" {
  count = var.ci_deploy_service_account_email != "" && var.env_enabled ? 1 : 0

  project = var.project_id
  role    = "roles/parametermanager.parameterViewer"
  member  = "serviceAccount:${var.ci_deploy_service_account_email}"
}

# IAM: each PM parameter → secretAccessor on its referenced secrets (for __REF__ resolution)
resource "google_secret_manager_secret_iam_member" "pm_secret_access" {
  for_each = local.pm_secret_bindings

  secret_id = google_secret_manager_secret.env_secrets[each.value.secret_name].id
  role      = "roles/secretmanager.secretAccessor"
  member    = google_parameter_manager_parameter.service_config[each.value.service].policy_member[0].iam_policy_uid_principal
}
