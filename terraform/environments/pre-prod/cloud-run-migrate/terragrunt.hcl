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

dependency "networking" {
  config_path = "../networking"

  mock_outputs = {
    vpc_id    = "projects/snip-491719/global/networks/snip-vpc-pre-prod"
    subnet_id = "projects/snip-491719/regions/me-west1/subnetworks/snip-subnet-pre-prod"
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
  vpc_id                = dependency.networking.outputs.vpc_id
  subnet_id             = dependency.networking.outputs.subnet_id

  secret_env_vars = {
    DATABASE_URL = dependency.secrets.outputs.database_url_secret_id
  }
}
