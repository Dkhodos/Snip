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

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}
