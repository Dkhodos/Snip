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

variable "job_name" {
  description = "Job name (used in resource naming: snip-{job_name}-{environment})"
  type        = string
}

variable "image" {
  description = "Docker image URL"
  type        = string
}

variable "service_account_email" {
  description = "Cloud Run service account email"
  type        = string
}

variable "cpu" {
  description = "CPU limit"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit"
  type        = string
  default     = "512Mi"
}

variable "env_vars" {
  description = "Plain environment variables (name → value)"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Secret Manager environment variables (name → secret_id)"
  type        = map(string)
  default     = {}
}
