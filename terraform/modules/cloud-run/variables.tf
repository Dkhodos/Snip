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

variable "service_name" {
  description = "Service name (used in resource naming: snip-{service_name}-{environment})"
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

# --- Optional VPC config (null = no VPC access) ---

variable "vpc_id" {
  description = "VPC network ID for Direct VPC Egress (null = disabled)"
  type        = string
  default     = null
}

variable "subnet_id" {
  description = "Subnet ID for Direct VPC Egress (required when vpc_id is set)"
  type        = string
  default     = null
}

# --- Container resources ---

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8080
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

# --- Scaling ---

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

# --- Environment variables ---

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

# --- Access control ---

variable "public" {
  description = "Whether to allow unauthenticated access (allUsers invoker)"
  type        = bool
  default     = true
}
