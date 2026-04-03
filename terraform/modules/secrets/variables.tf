variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "cloud_run_service_account_email" {
  description = "Cloud Run service account email"
  type        = string
}

variable "ci_deploy_service_account_email" {
  description = "CI deploy service account email (needs secretAccessor on Clerk publishable key for frontend builds)"
  type        = string
}
