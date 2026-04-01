output "workload_identity_provider" {
  description = "Full provider resource name — use this in GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "ci_service_account_email" {
  description = "CI deploy service account email — use this in GitHub Actions"
  value       = google_service_account.ci_deploy.email
}

output "ci_terraform_service_account_email" {
  description = "Terraform CI service account email — use in terraform.yml workflow"
  value       = google_service_account.ci_terraform.email
}
