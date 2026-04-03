locals {
  env_secret_names = toset([
    "snip-database-url-${var.environment}",
    "snip-clerk-publishable-${var.environment}",
    "snip-clerk-secret-${var.environment}",
    "snip-resend-api-key-${var.environment}",
  ])

  global_secret_names = toset([
    "snip-cloudflare-api-token",
  ])
}

# Per-environment secret containers — values are managed externally via gcloud,
# never by Terraform. To set or rotate a value:
#   gcloud secrets versions add <name> --data-file=-
resource "google_secret_manager_secret" "secrets" {
  for_each  = local.env_secret_names
  secret_id = each.key

  replication {
    auto {}
  }
}

# Global secret containers — shared across environments, values managed via gcloud.
resource "google_secret_manager_secret" "global_secrets" {
  for_each  = local.global_secret_names
  secret_id = each.key

  replication {
    auto {}
  }
}

# Cloud Run SA: read access to all env-specific secrets at runtime
resource "google_secret_manager_secret_iam_member" "cloud_run_access" {
  for_each = local.env_secret_names

  secret_id = google_secret_manager_secret.secrets[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account_email}"
}

# CI deploy SA: read access to Clerk publishable key for frontend Docker builds
resource "google_secret_manager_secret_iam_member" "ci_deploy_clerk_access" {
  secret_id = google_secret_manager_secret.secrets["snip-clerk-publishable-${var.environment}"].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.ci_deploy_service_account_email}"
}
