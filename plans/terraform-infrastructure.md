# Terraform Infrastructure Plan (Terragrunt)

> **Status:** Not started
> **Target:** Pre-prod only (prod folder exists but all modules `skip = true`)
> **Cost strategy:** Free tier everywhere except Cloud SQL (~$7-10/mo)
> **Weaker model note:** This plan includes exact file contents. Follow it step by step.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Folder Structure](#2-folder-structure)
3. [Step 0 — Bootstrap](#3-step-0--bootstrap)
4. [Step 1 — Root Terragrunt Config](#4-step-1--root-terragrunt-config)
5. [Step 2 — Environment Configs](#5-step-2--environment-configs)
6. [Step 3 — Project Module](#6-step-3--project-module)
7. [Step 4 — Networking Module](#7-step-4--networking-module)
8. [Step 5 — Database Module](#8-step-5--database-module)
9. [Step 6 — Secrets Module](#9-step-6--secrets-module)
10. [Step 7 — Cloud Run Backend Module](#10-step-7--cloud-run-backend-module)
11. [Step 7b — Cloud Run Frontend Module](#11-step-7b--cloud-run-frontend-module)
12. [Step 8 — CI/CD OIDC Module](#12-step-8--cicd-oidc-module)
13. [Step 9 — Prod (Disabled)](#13-step-9--prod-disabled)
14. [Step 10 — Dockerfiles](#14-step-10--dockerfiles)
15. [Step 11 — GitHub Actions Deploy](#15-step-11--github-actions-deploy)
16. [Execution Order](#16-execution-order)

---

## 1. Prerequisites

### Install tools

```bash
brew install terraform terragrunt
```

### Authenticate with GCP

```bash
# Login to GCP (opens browser)
gcloud auth login

# Set application default credentials (Terraform uses this)
gcloud auth application-default login

# Set your project
gcloud config set project <YOUR_PROJECT_ID>
```

### Required info before starting

You need to decide on:

| Variable | Example | Description |
|----------|---------|-------------|
| `project_id` | `snip-preprod` | GCP project ID |
| `region` | `me-west1` | GCP region (Israel) or `europe-west1` (Belgium, cheapest EU) |
| `billing_account` | from GCP Console | Must be linked to project |
| `github_org` | `your-github-username` | GitHub org/user for OIDC |
| `github_repo` | `Snip` | Repo name for OIDC |

---

## 2. Folder Structure

Create this exact structure:

```
terraform/
├── terragrunt.hcl
├── .terraform-version              # "1.9.8"
├── .terragrunt-version             # "0.68.0"
│
├── bootstrap/
│   ├── main.tf
│   └── variables.tf
│
├── _envcommon/
│   ├── project.hcl
│   ├── networking.hcl
│   ├── database.hcl
│   ├── cloud-run.hcl           # backend (FastAPI)
│   ├── cloud-run-frontend.hcl  # frontend (nginx)
│   ├── secrets.hcl
│   └── ci-oidc.hcl
│
├── modules/
│   ├── project/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── database/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloud-run/              # backend: has Secret Manager mounts + VPC
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloud-run-frontend/     # frontend: simple nginx, no secrets/VPC needed
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── secrets/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── ci-oidc/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
└── environments/
    ├── pre-prod/
    │   ├── env.hcl
    │   ├── project/
    │   │   └── terragrunt.hcl
    │   ├── networking/
    │   │   └── terragrunt.hcl
    │   ├── database/
    │   │   └── terragrunt.hcl
    │   ├── cloud-run/
    │   │   └── terragrunt.hcl
    │   ├── cloud-run-frontend/
    │   │   └── terragrunt.hcl
    │   ├── secrets/
    │   │   └── terragrunt.hcl
    │   └── ci-oidc/
    │       └── terragrunt.hcl
    └── prod/
        ├── env.hcl
        ├── project/
        │   └── terragrunt.hcl
        ├── networking/
        │   └── terragrunt.hcl
        ├── database/
        │   └── terragrunt.hcl
        ├── cloud-run/
        │   └── terragrunt.hcl
        ├── cloud-run-frontend/
        │   └── terragrunt.hcl
        ├── secrets/
        │   └── terragrunt.hcl
        └── ci-oidc/
            └── terragrunt.hcl
```

---

## 3. Step 0 — Bootstrap

The bootstrap creates the GCS bucket for Terraform remote state. This is plain Terraform (not Terragrunt) because the state bucket must exist before Terragrunt can use it.

### `terraform/bootstrap/variables.tf`

```hcl
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "me-west1"
}
```

### `terraform/bootstrap/main.tf`

```hcl
terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required API
resource "google_project_service" "storage" {
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

# GCS bucket for Terraform state
resource "google_storage_bucket" "tfstate" {
  name     = "${var.project_id}-tfstate"
  location = var.region

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.storage]
}
```

### How to run bootstrap

```bash
cd terraform/bootstrap
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID" -var="region=me-west1"
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="region=me-west1"
```

This creates a bucket named `YOUR_PROJECT_ID-tfstate`. State for bootstrap itself is local (committed to `.gitignore`).

---

## 4. Step 1 — Root Terragrunt Config

### `terraform/terragrunt.hcl`

```hcl
# Root terragrunt.hcl — inherited by all environments/modules

locals {
  # Parse the env.hcl from the environment directory
  env_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))

  project_id  = local.env_vars.locals.project_id
  region      = local.env_vars.locals.region
  environment = local.env_vars.locals.environment
}

# Auto-generate remote state config for each module
remote_state {
  backend = "gcs"
  config = {
    project  = local.project_id
    location = local.region
    bucket   = "${local.project_id}-tfstate"
    prefix   = "${local.environment}/${path_relative_to_include()}"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

# Generate provider config
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
EOF
}

# Common inputs passed to ALL modules
inputs = {
  project_id  = local.project_id
  region      = local.region
  environment = local.environment
}
```

### `terraform/.terraform-version`

```
1.9.8
```

### `terraform/.terragrunt-version`

```
0.68.0
```

---

## 5. Step 2 — Environment Configs

### `terraform/environments/pre-prod/env.hcl`

```hcl
locals {
  environment = "pre-prod"
  project_id  = "YOUR_PROJECT_ID"   # <-- REPLACE with actual GCP project ID
  region      = "me-west1"          # <-- Israel region, change if needed
}
```

### `terraform/environments/prod/env.hcl`

```hcl
locals {
  environment = "prod"
  project_id  = "YOUR_PROD_PROJECT_ID"  # <-- REPLACE when ready
  region      = "me-west1"
}
```

---

## 6. Step 3 — Project Module

This module enables all required GCP APIs and creates service accounts.

### `terraform/modules/project/variables.tf`

```hcl
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
```

### `terraform/modules/project/main.tf`

```hcl
# APIs to enable
locals {
  services = [
    "run.googleapis.com",              # Cloud Run
    "sqladmin.googleapis.com",         # Cloud SQL Admin
    "sql-component.googleapis.com",    # Cloud SQL
    "secretmanager.googleapis.com",    # Secret Manager
    "artifactregistry.googleapis.com", # Artifact Registry
    "vpcaccess.googleapis.com",        # Serverless VPC Access
    "compute.googleapis.com",          # Compute (needed for VPC)
    "servicenetworking.googleapis.com",# Service Networking (Private Service Access)
    "iam.googleapis.com",             # IAM
    "iamcredentials.googleapis.com",  # IAM Credentials (for OIDC)
    "cloudresourcemanager.googleapis.com", # Resource Manager
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.services)

  service            = each.value
  disable_on_destroy = false
}

# Service account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "snip-cloud-run-${var.environment}"
  display_name = "Snip Cloud Run (${var.environment})"
}

# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "snip-${var.environment}"
  format        = "DOCKER"
  description   = "Docker images for Snip ${var.environment}"

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}
```

### `terraform/modules/project/outputs.tf`

```hcl
output "cloud_run_service_account_email" {
  value = google_service_account.cloud_run.email
}

output "cloud_run_service_account_name" {
  value = google_service_account.cloud_run.name
}

output "artifact_registry_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
}

output "api_services" {
  value = [for s in google_project_service.apis : s.service]
}
```

### `terraform/_envcommon/project.hcl`

```hcl
terraform {
  source = "${dirname(find_in_parent_folders("terragrunt.hcl"))}//modules/project"
}
```

### `terraform/environments/pre-prod/project/terragrunt.hcl`

```hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/project.hcl"
  expose = true
}
```

---

## 7. Step 4 — Networking Module

Creates VPC, Private Service Access (for Cloud SQL private IP), and Serverless VPC Connector (Cloud Run → Cloud SQL).

### `terraform/modules/networking/variables.tf`

```hcl
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
```

### `terraform/modules/networking/main.tf`

```hcl
# VPC
resource "google_compute_network" "vpc" {
  name                    = "snip-vpc-${var.environment}"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "snip-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Private Service Access (Cloud SQL private IP)
resource "google_compute_global_address" "private_ip_range" {
  name          = "snip-private-ip-${var.environment}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

# Serverless VPC Connector (Cloud Run → private network)
resource "google_vpc_access_connector" "connector" {
  name          = "snip-vpc-cx-${var.environment}"
  region        = var.region
  network       = google_compute_network.vpc.id
  ip_cidr_range = "10.8.0.0/28"

  # Minimum resources to stay free-tier friendly
  min_instances = 2  # minimum allowed
  max_instances = 3
  machine_type  = "e2-micro"
}
```

### `terraform/modules/networking/outputs.tf`

```hcl
output "vpc_id" {
  value = google_compute_network.vpc.id
}

output "vpc_name" {
  value = google_compute_network.vpc.name
}

output "subnet_id" {
  value = google_compute_subnetwork.subnet.id
}

output "private_vpc_connection" {
  value = google_service_networking_connection.private_vpc_connection.id
}

output "vpc_connector_id" {
  value = google_vpc_access_connector.connector.id
}
```

### `terraform/_envcommon/networking.hcl`

```hcl
terraform {
  source = "${dirname(find_in_parent_folders("terragrunt.hcl"))}//modules/networking"
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    api_services = []
  }
}
```

### `terraform/environments/pre-prod/networking/terragrunt.hcl`

```hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/networking.hcl"
  expose = true
}
```

---

## 8. Step 5 — Database Module

Cloud SQL Postgres 15 — the only paid resource (~$7-10/mo for `db-f1-micro`).

### `terraform/modules/database/variables.tf`

```hcl
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
```

### `terraform/modules/database/main.tf`

```hcl
# Generate random password for DB user
resource "random_password" "db_password" {
  length  = 24
  special = false
}

# Cloud SQL instance
resource "google_sql_database_instance" "postgres" {
  name             = "snip-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "ZONAL"  # No HA — cost saving
    disk_size         = 10       # Minimum GB
    disk_autoresize   = false    # Prevent surprise costs

    ip_configuration {
      ipv4_enabled    = false           # No public IP
      private_network = var.vpc_id
    }

    backup_configuration {
      enabled = false  # No backups for pre-prod — cost saving
    }
  }

  deletion_protection = false  # Allow deletion for pre-prod

  depends_on = [var.private_vpc_connection]

  lifecycle {
    # Cloud SQL instance names cannot be reused for a week after deletion.
    # If you need to recreate, change the name.
    ignore_changes = [name]
  }
}

# Database
resource "google_sql_database" "shortener" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

# User
resource "google_sql_user" "app_user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}
```

### `terraform/modules/database/outputs.tf`

```hcl
output "instance_name" {
  value = google_sql_database_instance.postgres.name
}

output "instance_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}

output "private_ip" {
  value = google_sql_database_instance.postgres.private_ip_address
}

output "db_name" {
  value = google_sql_database.shortener.name
}

output "db_user" {
  value = google_sql_user.app_user.name
}

output "db_password" {
  value     = random_password.db_password.result
  sensitive = true
}

# Full connection string for the app (asyncpg format)
output "database_url" {
  value     = "postgresql+asyncpg://${google_sql_user.app_user.name}:${random_password.db_password.result}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.shortener.name}"
  sensitive = true
}
```

### `terraform/_envcommon/database.hcl`

```hcl
terraform {
  source = "${dirname(find_in_parent_folders("terragrunt.hcl"))}//modules/database"
}

dependency "networking" {
  config_path = "../networking"

  mock_outputs = {
    vpc_id                 = "mock-vpc-id"
    private_vpc_connection = "mock-connection"
  }
}

inputs = {
  vpc_id                 = dependency.networking.outputs.vpc_id
  private_vpc_connection = dependency.networking.outputs.private_vpc_connection
}
```

### `terraform/environments/pre-prod/database/terragrunt.hcl`

```hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/database.hcl"
  expose = true
}

# Pre-prod specific: cheapest tier, no HA
inputs = {
  db_tier = "db-f1-micro"
}
```

---

## 9. Step 6 — Secrets Module

Stores secrets in GCP Secret Manager and grants Cloud Run access to read them.

### `terraform/modules/secrets/variables.tf`

```hcl
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
```

### `terraform/modules/secrets/main.tf`

```hcl
locals {
  secrets = {
    "snip-database-url-${var.environment}"        = var.database_url
    "snip-clerk-publishable-${var.environment}"    = var.clerk_publishable_key
    "snip-clerk-secret-${var.environment}"         = var.clerk_secret_key
  }
}

# Create secrets
resource "google_secret_manager_secret" "secrets" {
  for_each  = local.secrets
  secret_id = each.key

  replication {
    auto {}
  }
}

# Create secret versions (the actual values)
resource "google_secret_manager_secret_version" "versions" {
  for_each = local.secrets

  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = each.value
}

# Grant Cloud Run SA access to read all secrets
resource "google_secret_manager_secret_iam_member" "cloud_run_access" {
  for_each = local.secrets

  secret_id = google_secret_manager_secret.secrets[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account_email}"
}
```

### `terraform/modules/secrets/outputs.tf`

```hcl
output "database_url_secret_id" {
  value = google_secret_manager_secret.secrets["snip-database-url-${var.environment}"].secret_id
}

output "clerk_publishable_secret_id" {
  value = google_secret_manager_secret.secrets["snip-clerk-publishable-${var.environment}"].secret_id
}

output "clerk_secret_secret_id" {
  value = google_secret_manager_secret.secrets["snip-clerk-secret-${var.environment}"].secret_id
}
```

### `terraform/_envcommon/secrets.hcl`

```hcl
terraform {
  source = "${dirname(find_in_parent_folders("terragrunt.hcl"))}//modules/secrets"
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock@mock.iam.gserviceaccount.com"
  }
}

dependency "database" {
  config_path = "../database"

  mock_outputs = {
    database_url = "postgresql+asyncpg://mock:mock@127.0.0.1:5432/mock"
  }
}

inputs = {
  cloud_run_service_account_email = dependency.project.outputs.cloud_run_service_account_email
  database_url                    = dependency.database.outputs.database_url
}
```

### `terraform/environments/pre-prod/secrets/terragrunt.hcl`

**IMPORTANT:** The Clerk keys must be provided via `terraform.tfvars` or command line. Do NOT commit real keys.

```hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/secrets.hcl"
  expose = true
}

# Clerk keys — pass via CLI or terraform.tfvars (NEVER commit)
# terragrunt apply -var="clerk_publishable_key=pk_test_..." -var="clerk_secret_key=sk_test_..."
inputs = {
  clerk_publishable_key = ""  # Override via -var or TF_VAR_
  clerk_secret_key      = ""  # Override via -var or TF_VAR_
}
```

---

## 10. Step 7 — Cloud Run Backend Module

Deploys the dashboard-backend as a Cloud Run service.

### `terraform/modules/cloud-run/variables.tf`

```hcl
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

variable "vpc_connector_id" {
  description = "Serverless VPC connector ID"
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
```

### `terraform/modules/cloud-run/main.tf`

```hcl
resource "google_cloud_run_v2_service" "backend" {
  name     = "snip-backend-${var.environment}"
  location = var.region

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    vpc_access {
      connector = var.vpc_connector_id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true  # CPU throttled when not processing requests (cost saving)
      }

      # Environment variables from Secret Manager
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = var.database_url_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "CLERK_PUBLISHABLE_KEY"
        value_source {
          secret_key_ref {
            secret  = var.clerk_publishable_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "CLERK_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.clerk_secret_secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment == "prod" ? "production" : "staging"
      }
    }
  }

  # Allow unauthenticated access (public API)
  deletion_protection = false
}

# Make the service publicly accessible (no auth required to call the API)
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.backend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### `terraform/modules/cloud-run/outputs.tf`

```hcl
output "service_url" {
  value = google_cloud_run_v2_service.backend.uri
}

output "service_name" {
  value = google_cloud_run_v2_service.backend.name
}
```

### `terraform/_envcommon/cloud-run.hcl`

```hcl
terraform {
  source = "${dirname(find_in_parent_folders("terragrunt.hcl"))}//modules/cloud-run"
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock@mock.iam.gserviceaccount.com"
    artifact_registry_url           = "me-west1-docker.pkg.dev/mock/snip-pre-prod"
  }
}

dependency "networking" {
  config_path = "../networking"

  mock_outputs = {
    vpc_connector_id = "mock-connector"
  }
}

dependency "secrets" {
  config_path = "../secrets"

  mock_outputs = {
    database_url_secret_id        = "mock-db-url"
    clerk_publishable_secret_id   = "mock-clerk-pub"
    clerk_secret_secret_id        = "mock-clerk-secret"
  }
}

inputs = {
  service_account_email       = dependency.project.outputs.cloud_run_service_account_email
  vpc_connector_id            = dependency.networking.outputs.vpc_connector_id
  database_url_secret_id      = dependency.secrets.outputs.database_url_secret_id
  clerk_publishable_secret_id = dependency.secrets.outputs.clerk_publishable_secret_id
  clerk_secret_secret_id      = dependency.secrets.outputs.clerk_secret_secret_id
}
```

### `terraform/environments/pre-prod/cloud-run/terragrunt.hcl`

```hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/cloud-run.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"
}

inputs = {
  # Initial image — use a placeholder until first CI/CD deploy
  # After first deploy, this will be managed by CI/CD, not Terraform
  image = "${dependency.project.outputs.artifact_registry_url}/dashboard-backend:latest"

  # Scale to zero — free when idle
  min_instances = 0
  max_instances = 2
}
```

---

## 11. Step 7b — Cloud Run Frontend Module

Deploys the dashboard-frontend as a second Cloud Run service (nginx serving the Vite build).

The frontend is **stateless** — no database access, no Secret Manager mounts, no VPC connector needed. `VITE_*` env vars are baked into the bundle at Docker build time (CI passes them as `--build-arg`).

### `terraform/modules/cloud-run-frontend/variables.tf`

```hcl
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
  description = "Docker image URL for the frontend nginx container"
  type        = string
}

variable "service_account_email" {
  description = "Cloud Run service account email"
  type        = string
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
```

### `terraform/modules/cloud-run-frontend/main.tf`

```hcl
resource "google_cloud_run_v2_service" "frontend" {
  name     = "snip-frontend-${var.environment}"
  location = var.region

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # No VPC connector — nginx only serves static files, no DB access
    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
        cpu_idle = true
      }
    }
  }

  deletion_protection = false
}

# Public access
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.frontend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### `terraform/modules/cloud-run-frontend/outputs.tf`

```hcl
output "service_url" {
  value = google_cloud_run_v2_service.frontend.uri
}

output "service_name" {
  value = google_cloud_run_v2_service.frontend.name
}
```

### `terraform/_envcommon/cloud-run-frontend.hcl`

```hcl
terraform {
  source = "${dirname(find_in_parent_folders("terragrunt.hcl"))}//modules/cloud-run-frontend"
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock@mock.iam.gserviceaccount.com"
    artifact_registry_url           = "me-west1-docker.pkg.dev/mock/snip-pre-prod"
  }
}

inputs = {
  service_account_email = dependency.project.outputs.cloud_run_service_account_email
}
```

### `terraform/environments/pre-prod/cloud-run-frontend/terragrunt.hcl`

```hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/cloud-run-frontend.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"
}

inputs = {
  # Initial image — use a placeholder until first CI/CD deploy
  image         = "${dependency.project.outputs.artifact_registry_url}/dashboard-frontend:latest"
  min_instances = 0
  max_instances = 2
}
```

> **Note:** `VITE_CLERK_PUBLISHABLE_KEY` and `VITE_API_URL` are **not** Cloud Run env vars — they are baked into the bundle by Vite during the Docker build. CI/CD passes them as `--build-arg` (see Step 11).

---

## 12. Step 8 — CI/CD OIDC Module

Workload Identity Federation allows GitHub Actions to authenticate to GCP without long-lived service account keys.

### `terraform/modules/ci-oidc/variables.tf`

```hcl
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

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "cloud_run_service_account_email" {
  description = "Cloud Run service account to impersonate for deploys"
  type        = string
}
```

### `terraform/modules/ci-oidc/main.tf`

```hcl
# Workload Identity Pool
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-pool-${var.environment}"
  display_name              = "GitHub Actions Pool (${var.environment})"
}

# Workload Identity Provider (GitHub OIDC)
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Actions Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  attribute_condition = "assertion.repository == '${var.github_org}/${var.github_repo}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Service account for CI/CD deployments
resource "google_service_account" "ci_deploy" {
  account_id   = "snip-ci-deploy-${var.environment}"
  display_name = "Snip CI Deploy (${var.environment})"
}

# Allow GitHub Actions to impersonate the CI service account
resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.ci_deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_org}/${var.github_repo}"
}

# Permissions for CI service account

# Push Docker images to Artifact Registry
resource "google_project_iam_member" "ci_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.ci_deploy.email}"
}

# Deploy to Cloud Run
resource "google_project_iam_member" "ci_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.ci_deploy.email}"
}

# Allow CI SA to act as the Cloud Run SA (needed for deploy)
resource "google_service_account_iam_member" "ci_acts_as_cloud_run" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/${var.cloud_run_service_account_email}"
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.ci_deploy.email}"
}
```

### `terraform/modules/ci-oidc/outputs.tf`

```hcl
output "workload_identity_provider" {
  description = "Full provider resource name — use this in GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "ci_service_account_email" {
  description = "CI deploy service account email — use this in GitHub Actions"
  value       = google_service_account.ci_deploy.email
}
```

### `terraform/_envcommon/ci-oidc.hcl`

```hcl
terraform {
  source = "${dirname(find_in_parent_folders("terragrunt.hcl"))}//modules/ci-oidc"
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock@mock.iam.gserviceaccount.com"
  }
}

inputs = {
  cloud_run_service_account_email = dependency.project.outputs.cloud_run_service_account_email
}
```

### `terraform/environments/pre-prod/ci-oidc/terragrunt.hcl`

```hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/ci-oidc.hcl"
  expose = true
}

inputs = {
  github_org  = "YOUR_GITHUB_ORG"   # <-- REPLACE
  github_repo = "Snip"
}
```

---

## 13. Step 9 — Prod (Disabled)

Every module in `prod/` has `skip = true`. This means `terragrunt run-all plan` in prod does nothing.

### Template for ALL prod modules

Each file under `terraform/environments/prod/*/terragrunt.hcl` should be:

```hcl
# Prod is disabled — remove skip = true when ready to deploy
skip = true

include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/MODULE_NAME.hcl"
  expose = true
}
```

Replace `MODULE_NAME` with the module name (`project`, `networking`, `database`, `cloud-run`, `cloud-run-frontend`, `secrets`, `ci-oidc`).

For example, `terraform/environments/prod/database/terragrunt.hcl`:

```hcl
skip = true

include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("terragrunt.hcl"))}/_envcommon/database.hcl"
  expose = true
}
```

---

## 14. Step 10 — Dockerfiles

Both services have Dockerfiles. Build context is always the **monorepo root**.

### Backend — `apps/dashboard-backend/Dockerfile` ✅ (already created)

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY packages/db/ packages/db/
COPY packages/email/ packages/email/
COPY packages/auth/ packages/auth/

COPY apps/dashboard-backend/ apps/dashboard-backend/

RUN cd apps/dashboard-backend && uv sync --frozen --no-dev

CMD ["uv", "run", "--no-sync", "--directory", "apps/dashboard-backend", \
     "uvicorn", "dashboard_backend.main:app", \
     "--host", "0.0.0.0", "--port", "8080"]
```

### Frontend — `apps/dashboard-frontend/Dockerfile` ✅ (already created)

Multi-stage: Node 20 (pnpm build) → nginx:alpine (serve dist/).

`VITE_CLERK_PUBLISHABLE_KEY` and `VITE_API_URL` are Docker `ARG`s — baked into the bundle by Vite at build time. CI passes them via `--build-arg` (not Cloud Run env vars).

```dockerfile
# Build stage
FROM node:25-slim AS builder

RUN corepack enable

WORKDIR /app

COPY apps/dashboard-frontend/package.json apps/dashboard-frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY apps/dashboard-frontend/ .

ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_API_URL

RUN pnpm build

# Serve stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY apps/dashboard-frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```

`apps/dashboard-frontend/nginx.conf` configures SPA routing (`try_files`), immutable asset caching, and no-cache for `index.html`.

---

## 15. Step 11 — GitHub Actions Deploy

Two deploy jobs — one per service, triggered on push to `main`.

### Backend — add to `.github/workflows/dashboard-backend.yml`

```yaml
  deploy:
    name: Deploy to Pre-prod
    needs: lint-and-test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write

    env:
      PROJECT_ID: YOUR_PROJECT_ID         # <-- REPLACE
      REGION: me-west1                     # <-- REPLACE if different
      SERVICE: snip-backend-pre-prod
      REPO: snip-pre-prod

    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: "projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool-pre-prod/providers/github-provider"  # <-- REPLACE PROJECT_NUMBER
          service_account: "snip-ci-deploy-pre-prod@YOUR_PROJECT_ID.iam.gserviceaccount.com"  # <-- REPLACE

      - uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev --quiet

      - name: Build and push Docker image
        run: |
          IMAGE="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO }}/dashboard-backend:${{ github.sha }}"
          docker build -t "$IMAGE" -f apps/dashboard-backend/Dockerfile .
          docker push "$IMAGE"

      - name: Deploy to Cloud Run
        run: |
          IMAGE="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO }}/dashboard-backend:${{ github.sha }}"
          gcloud run deploy ${{ env.SERVICE }} \
            --image "$IMAGE" \
            --region ${{ env.REGION }} \
            --quiet
```

### Frontend — add to `.github/workflows/dashboard-frontend.yml`

Note: `VITE_API_URL` is the backend Cloud Run URL (available after Terraform runs). Store both as GitHub Actions secrets.

```yaml
  deploy:
    name: Deploy to Pre-prod
    needs: lint-and-test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write

    env:
      PROJECT_ID: YOUR_PROJECT_ID         # <-- REPLACE
      REGION: me-west1                     # <-- REPLACE if different
      SERVICE: snip-frontend-pre-prod
      REPO: snip-pre-prod

    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: "projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool-pre-prod/providers/github-provider"  # <-- REPLACE PROJECT_NUMBER
          service_account: "snip-ci-deploy-pre-prod@YOUR_PROJECT_ID.iam.gserviceaccount.com"  # <-- REPLACE

      - uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev --quiet

      - name: Build and push Docker image
        run: |
          IMAGE="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO }}/dashboard-frontend:${{ github.sha }}"
          docker build \
            --build-arg VITE_CLERK_PUBLISHABLE_KEY="${{ secrets.VITE_CLERK_PUBLISHABLE_KEY }}" \
            --build-arg VITE_API_URL="${{ secrets.VITE_API_URL }}" \
            -t "$IMAGE" \
            -f apps/dashboard-frontend/Dockerfile .
          docker push "$IMAGE"

      - name: Deploy to Cloud Run
        run: |
          IMAGE="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO }}/dashboard-frontend:${{ github.sha }}"
          gcloud run deploy ${{ env.SERVICE }} \
            --image "$IMAGE" \
            --region ${{ env.REGION }} \
            --quiet
```

**GitHub Actions secrets required:**
| Secret | Value |
|--------|-------|
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key for pre-prod |
| `VITE_API_URL` | Backend Cloud Run URL (e.g. `https://snip-backend-pre-prod-xxxx.run.app`) |

---

## 16. Execution Order

Run these steps **in order**. Each step must complete before the next.

```bash
# 0. Bootstrap (one-time)
cd terraform/bootstrap
terraform init
terraform apply -var="project_id=YOUR_PROJECT_ID"

# 1. Deploy pre-prod modules in dependency order
cd terraform/environments/pre-prod

# Option A: All at once (Terragrunt handles dependency order)
terragrunt run-all apply

# Option B: One at a time (if you want to verify each step)
cd project    && terragrunt apply && cd ..
cd networking && terragrunt apply && cd ..
cd database   && terragrunt apply && cd ..
cd secrets    && terragrunt apply -var="clerk_publishable_key=pk_test_..." -var="clerk_secret_key=sk_test_..." && cd ..
cd cloud-run          && terragrunt apply && cd ..
cd cloud-run-frontend && terragrunt apply && cd ..
cd ci-oidc            && terragrunt apply && cd ..

# 2. Verify
terragrunt run-all output

# 3. Run Alembic migrations against Cloud SQL
# (from your local machine, using Cloud SQL Auth Proxy)
# Install: https://cloud.google.com/sql/docs/postgres/sql-proxy
cloud-sql-proxy YOUR_PROJECT_ID:REGION:snip-db-pre-prod --port=5433 &
DATABASE_URL="postgresql+asyncpg://shortener_app:PASSWORD@127.0.0.1:5433/shortener" \
  cd packages/db && uv run alembic upgrade head
```

---

## Gitignore additions

Add to root `.gitignore`:

```
# Terraform
terraform/**/.terraform/
terraform/**/*.tfstate
terraform/**/*.tfstate.backup
terraform/**/.terragrunt-cache/
terraform/**/*.tfvars
!terraform/**/*.tfvars.example
terraform/bootstrap/terraform.tfstate*
```

---

## Placeholders to Replace

Search for these before running:

| Placeholder | Where | What |
|-------------|-------|------|
| `YOUR_PROJECT_ID` | `env.hcl`, bootstrap, GitHub Actions | Your GCP project ID |
| `YOUR_PROD_PROJECT_ID` | `prod/env.hcl` | Prod GCP project ID (when ready) |
| `YOUR_GITHUB_ORG` | `ci-oidc/terragrunt.hcl` | GitHub username or org |
| `PROJECT_NUMBER` | GitHub Actions workflow | GCP project number (numeric, from Console) |
| `me-west1` | Everywhere | Change if not using Israel region |
| Clerk keys | `secrets/terragrunt.hcl` | Real Clerk keys via `-var` flags |
| `VITE_CLERK_PUBLISHABLE_KEY` | GitHub Actions secret | Clerk publishable key for pre-prod |
| `VITE_API_URL` | GitHub Actions secret | Backend Cloud Run URL (get from `terragrunt output` after deploy) |
