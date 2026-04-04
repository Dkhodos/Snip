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

variable "image_versions_to_keep" {
  description = "Number of most recent image versions to retain per image in Artifact Registry. Older versions are deleted automatically."
  type        = number
  default     = 3
}
