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

variable "vpc_id" {
  description = "VPC network ID"
  type        = string
}

variable "private_vpc_connection" {
  description = "Private VPC connection ID (ensures peering is ready)"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "shortener"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "shortener_app"
}

variable "db_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-f1-micro"
}
