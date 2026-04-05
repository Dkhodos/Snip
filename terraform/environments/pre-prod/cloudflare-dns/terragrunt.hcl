include "root" {
  path           = find_in_parent_folders("root.hcl")
  merge_strategy = "deep"
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/cloudflare-dns.hcl"
  expose = true
}

# Override the generated provider block to include both google and cloudflare
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
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "cloudflare" {
  # Reads CLOUDFLARE_API_TOKEN from environment
}
EOF
}

dependency "cloud_run" {
  config_path = "../cloud-run"

  mock_outputs = {
    service_name = "snip-backend-pre-prod"
  }
}

dependency "cloud_run_frontend" {
  config_path = "../cloud-run-frontend"

  mock_outputs = {
    service_name = "snip-frontend-pre-prod"
  }
}

dependency "cloud_run_redirect" {
  config_path = "../cloud-run-redirect"

  mock_outputs = {
    service_name = "snip-redirect-pre-prod"
  }
}

inputs = {
  cloudflare_zone_id     = get_env("CLOUDFLARE_ZONE_ID")
  domain                 = get_env("DOMAIN")
  frontend_service_name  = dependency.cloud_run_frontend.outputs.service_name
  backend_service_name   = dependency.cloud_run.outputs.service_name
  redirect_service_name  = dependency.cloud_run_redirect.outputs.service_name
}
