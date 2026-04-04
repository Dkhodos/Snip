variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name (pre-prod, prod)"
  type        = string
}

variable "devops_root" {
  description = "Absolute path to the .devops/ directory"
  type        = string
}

variable "services" {
  description = "List of service names to process (must match directory names in .devops/values/{env}/)"
  type        = list(string)
}

variable "cloud_run_service_account_email" {
  description = "Cloud Run service account email — granted secretAccessor on all env secrets"
  type        = string
}

variable "ci_deploy_service_account_email" {
  description = "CI deploy service account email — granted parameterViewer for PM reads"
  type        = string
  default     = ""
}

variable "env_enabled" {
  description = "Whether to upload config to Parameter Manager (false = count 0, nothing created in PM)"
  type        = bool
  default     = true
}

variable "manage_secrets" {
  description = "Whether this module creates Secret Manager resources (false = SM stays in secrets/ module during migration)"
  type        = bool
  default     = false
}
