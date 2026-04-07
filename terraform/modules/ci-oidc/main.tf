# GitHub Actions OIDC federation and CI service accounts.

# Workload Identity Pool
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-pool-${var.environment}"
  display_name              = "GitHub Actions Pool (${var.environment})"
}

# Workload Identity Provider (GitHub OIDC)
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Actions Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  attribute_condition = "assertion.repository == '${var.github_org}/${var.github_repo}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# ---------------------------------------------------------------------------
# Deploy Service Account (push images + deploy Cloud Run)
# ---------------------------------------------------------------------------

resource "google_service_account" "ci_deploy" {
  account_id   = "snip-ci-deploy-${var.environment}"
  display_name = "Snip CI Deploy (${var.environment})"
}

resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.ci_deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_org}/${var.github_repo}"
}

resource "google_project_iam_member" "ci_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.ci_deploy.email}"
}

resource "google_project_iam_member" "ci_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.ci_deploy.email}"
}

resource "google_project_iam_member" "ci_logging_viewer" {
  project = var.project_id
  role    = "roles/logging.viewer"
  member  = "serviceAccount:${google_service_account.ci_deploy.email}"
}

resource "google_service_account_iam_member" "ci_acts_as_cloud_run" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/${var.cloud_run_service_account_email}"
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.ci_deploy.email}"
}

# ---------------------------------------------------------------------------
# Terraform CI Service Account (plan + apply infrastructure)
# ---------------------------------------------------------------------------

resource "google_service_account" "ci_terraform" {
  account_id   = "snip-terraform-ci-${var.environment}"
  display_name = "Snip Terraform CI (${var.environment})"
}

resource "google_service_account_iam_member" "terraform_workload_identity" {
  service_account_id = google_service_account.ci_terraform.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_org}/${var.github_repo}"
}

locals {
  terraform_ci_roles = [
    "roles/editor",
    "roles/iam.securityAdmin",
    "roles/secretmanager.admin",
    "roles/iam.workloadIdentityPoolAdmin",
  ]
}

resource "google_project_iam_member" "ci_terraform_roles" {
  for_each = toset(local.terraform_ci_roles)
  project  = var.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.ci_terraform.email}"
}
