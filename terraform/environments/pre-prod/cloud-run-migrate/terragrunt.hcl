include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/cloud-run-migrate.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock-sa@snip-491719.iam.gserviceaccount.com"
    artifact_registry_url           = "me-west1-docker.pkg.dev/mock/snip-pre-prod"
  }
}

dependency "secrets" {
  config_path = "../secrets"

  mock_outputs = {
    database_url_secret_id = "mock-db-url"
  }
}

inputs = {
  job_name              = "migrate"
  image                 = "gcr.io/cloudrun/hello"
  service_account_email = dependency.project.outputs.cloud_run_service_account_email

  secret_env_vars = {
    DATABASE_URL = dependency.secrets.outputs.database_url_secret_id
  }
}
