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

dependency "cloud_run" {
  config_path = "../cloud-run"

  mock_outputs = {
    service_url = "https://snip-backend-pre-prod-mock.run.app"
  }
}

dependency "config" {
  config_path = "../config"

  mock_outputs = {
    env_vars = {
      frontend = {}
    }
  }
}

inputs = {
  service_name          = "frontend"
  image                 = "gcr.io/cloudrun/hello"
  memory                = "256Mi"
  min_instances         = 0
  max_instances         = 2
  service_account_email = dependency.project.outputs.cloud_run_service_account_email

  # Merge static YAML config with dynamic cross-service values
  env_vars = merge(
    dependency.config.outputs.env_vars["frontend"],
    { BACKEND_URL = dependency.cloud_run.outputs.service_url },
  )
}
