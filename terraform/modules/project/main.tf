# GCP API enablement, service account, and Artifact Registry.

# APIs to enable
locals {
  services = [
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "sql-component.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.services)

  service            = each.value
  disable_on_destroy = false
}

# Service account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "snip-cloud-run-${var.environment}"
  display_name = "Snip Cloud Run (${var.environment})"
}

# Look up project number
data "google_project" "current" {}

# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "snip-${var.environment}"
  format        = "DOCKER"
  description   = "Docker images for Snip ${var.environment}"

  # Keep only the N most recent image versions; older digests are deleted automatically.
  cleanup_policies {
    id     = "keep-recent-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count = var.image_versions_to_keep
    }
  }
  cleanup_policy_dry_run = false

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}

# Artifact Registry repository for shared base Docker images (environment-agnostic)
resource "google_artifact_registry_repository" "base" {
  location      = var.region
  repository_id = "snip-base"
  format        = "DOCKER"
  description   = "Shared base Docker images for Snip"

  cleanup_policies {
    id     = "keep-recent-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count = var.image_versions_to_keep
    }
  }
  cleanup_policy_dry_run = false

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}
