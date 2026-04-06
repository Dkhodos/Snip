# GCS bucket for OG preview images (publicly readable, written by Cloud Run).

#checkov:skip=CKV_GCP_78:Versioning not needed for generated OG images — they are regenerated on demand
#checkov:skip=CKV_GCP_114:Bucket must be publicly readable so social crawlers can fetch OG images
resource "google_storage_bucket" "og_images" {
  name          = "snip-og-images-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"
  project       = var.project_id

  # Uniform bucket-level access required for allUsers IAM binding
  uniform_bucket_level_access = true

  # Versioning not needed for generated assets
  versioning {
    enabled = false
  }

  # Clean up images for deleted/expired links after 90 days
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Public read — allows social crawlers to fetch OG images directly
#checkov:skip=CKV_GCP_28:Public read is intentional — social crawlers fetch OG images via direct URL
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.og_images.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Cloud Run SA can create and overwrite objects (for regeneration)
resource "google_storage_bucket_iam_member" "cloud_run_write" {
  bucket = google_storage_bucket.og_images.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.cloud_run_service_account_email}"
}
