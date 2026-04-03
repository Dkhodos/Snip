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

variable "project_number" {
  description = "GCP project number (for Pub/Sub service agent)"
  type        = string
}

variable "cloud_run_service_account_email" {
  description = "Cloud Run service account email (publisher)"
  type        = string
}

variable "push_service_account_email" {
  description = "Service account for Pub/Sub push OIDC token"
  type        = string
  default     = ""
}

variable "click_worker_endpoint" {
  description = "Click worker Cloud Run URL for push subscription (empty = skip push sub)"
  type        = string
  default     = ""
}
