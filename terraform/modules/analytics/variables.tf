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
  description = "Cloud Run service account email (editor + viewer)"
  type        = string
}
