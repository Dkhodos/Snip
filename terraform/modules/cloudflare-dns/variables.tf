variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., pre-prod)"
  type        = string
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID for the domain"
  type        = string
}

variable "domain" {
  description = "Base domain (e.g., snip-app.win)"
  type        = string
}

variable "frontend_service_name" {
  description = "Cloud Run frontend service name"
  type        = string
}

variable "backend_service_name" {
  description = "Cloud Run backend service name"
  type        = string
}

variable "redirect_service_name" {
  description = "Cloud Run redirect service name (null = skip redirect DNS)"
  type        = string
  default     = null
}
