output "bucket_name" {
  description = "Name of the OG images GCS bucket"
  value       = google_storage_bucket.og_images.name
}

output "bucket_public_url_base" {
  description = "Public URL base for OG images (without trailing slash)"
  value       = "https://storage.googleapis.com/${google_storage_bucket.og_images.name}"
}
