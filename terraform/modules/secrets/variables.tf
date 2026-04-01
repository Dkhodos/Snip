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

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "clerk_publishable_key" {
  description = "Clerk publishable key"
  type        = string
  sensitive   = true
}

variable "clerk_secret_key" {
  description = "Clerk secret key"
  type        = string
  sensitive   = true
}

variable "resend_api_key" {
  description = "Resend API key for production email"
  type        = string
  sensitive   = true
}
