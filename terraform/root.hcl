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
