include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/cloud-run.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock-sa@snip-491719.iam.gserviceaccount.com"
    artifact_registry_url           = "me-west1-docker.pkg.dev/mock/snip-pre-prod"
  }
}

dependency "networking" {
  config_path = "../networking"

  mock_outputs = {
    vpc_id    = "projects/snip-491719/global/networks/snip-vpc-pre-prod"
    subnet_id = "projects/snip-491719/regions/me-west1/subnetworks/snip-subnet-pre-prod"
  }
}

dependency "config" {
  config_path = "../config"

  mock_outputs = {
    env_vars = {
      backend = {
        ENVIRONMENT     = "staging"
        EMAIL_PROVIDER  = "resend"
        EMAIL_FROM      = "Snip <noreply@snip.dev>"
        CLICK_THRESHOLD = "100"
        ALLOWED_ORIGINS = "https://app.pre-prod.snip-app.win,http://localhost:5173"
      }
    }
    secret_env_vars = {
      backend = {
        DATABASE_URL     = "mock-db-url"
        CLERK_SECRET_KEY = "mock-clerk-secret"
        RESEND_API_KEY   = "mock-resend-key"
      }
    }
  }
}

inputs = {
  service_name          = "backend"
  image                 = "gcr.io/cloudrun/hello"
  min_instances         = 0
  max_instances         = 2
  service_account_email = dependency.project.outputs.cloud_run_service_account_email
  vpc_id                = dependency.networking.outputs.vpc_id
  subnet_id             = dependency.networking.outputs.subnet_id

  env_vars        = dependency.config.outputs.env_vars["backend"]
  secret_env_vars = dependency.config.outputs.secret_env_vars["backend"]
}
