terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required API
resource "google_project_service" "storage" {
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

# GCS bucket for Terraform state
resource "google_storage_bucket" "tfstate" {
  name     = "${var.project_id}-tfstate"
  location = var.region

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.storage]
}
