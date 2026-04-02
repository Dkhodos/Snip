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

variable "image" {
  description = "Docker image URL (e.g., REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG)"
  type        = string
}

variable "service_account_email" {
  description = "Cloud Run service account email"
  type        = string
}

variable "vpc_id" {
  description = "VPC network ID for Direct VPC Egress"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for Direct VPC Egress"
  type        = string
}

variable "database_url_secret_id" {
  description = "Secret Manager secret ID for DATABASE_URL"
  type        = string
}

variable "clerk_publishable_secret_id" {
  description = "Secret Manager secret ID for CLERK_PUBLISHABLE_KEY"
  type        = string
}

variable "clerk_secret_secret_id" {
  description = "Secret Manager secret ID for CLERK_SECRET_KEY"
  type        = string
}

variable "resend_api_key_secret_id" {
  description = "Secret Manager secret ID for RESEND_API_KEY"
  type        = string
}

variable "email_provider" {
  description = "Email provider (resend or mailpit)"
  type        = string
  default     = "resend"
}

variable "email_from" {
  description = "Email sender address"
  type        = string
  default     = "Snip <noreply@snip.dev>"
}

variable "click_threshold" {
  description = "Click count threshold for notifications"
  type        = number
  default     = 100
}

variable "allowed_origins" {
  description = "Comma-separated list of allowed CORS origins"
  type        = string
  default     = "http://localhost:5173"
}

variable "min_instances" {
  description = "Minimum number of instances (0 = scale to zero)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 2
}
