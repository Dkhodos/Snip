locals {
  secrets = {
    "snip-database-url-${var.environment}"     = var.database_url
    "snip-clerk-publishable-${var.environment}" = var.clerk_publishable_key
    "snip-clerk-secret-${var.environment}"      = var.clerk_secret_key
    "snip-resend-api-key-${var.environment}"    = var.resend_api_key
  }
}

# Create secrets
resource "google_secret_manager_secret" "secrets" {
  for_each  = local.secrets
  secret_id = each.key

  replication {
    auto {}
  }
}

# Create secret versions (the actual values)
resource "google_secret_manager_secret_version" "versions" {
  for_each = local.secrets

  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = each.value

  # Prevent CI from overwriting secrets with empty strings after initial apply.
  # Rotate secrets manually via gcloud or a targeted local apply.
  lifecycle {
    ignore_changes = [secret_data]
  }
}

# Grant Cloud Run SA access to read all secrets
resource "google_secret_manager_secret_iam_member" "cloud_run_access" {
  for_each = local.secrets

  secret_id = google_secret_manager_secret.secrets[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account_email}"
}
