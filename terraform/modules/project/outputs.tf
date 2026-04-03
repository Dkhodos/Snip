output "cloud_run_service_account_email" {
  value = google_service_account.cloud_run.email
}

output "cloud_run_service_account_name" {
  value = google_service_account.cloud_run.name
}

output "artifact_registry_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
}

output "api_services" {
  value = [for s in google_project_service.apis : s.service]
}

output "project_number" {
  value = data.google_project.current.number
}
