variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for the bucket"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. pre-prod, prod)"
  type        = string
}

variable "cloud_run_service_account_email" {
  description = "Email of the Cloud Run service account that will read/write OG images"
  type        = string
}
