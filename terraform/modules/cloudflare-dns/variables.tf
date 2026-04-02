variable "project_id" {
  description = "GCP project ID (passed by root.hcl, unused)"
  type        = string
}

variable "region" {
  description = "GCP region (passed by root.hcl, unused)"
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

variable "frontend_origin_host" {
  description = "Cloud Run frontend .run.app hostname (without https://)"
  type        = string
}

variable "backend_origin_host" {
  description = "Cloud Run backend .run.app hostname (without https://)"
  type        = string
}
