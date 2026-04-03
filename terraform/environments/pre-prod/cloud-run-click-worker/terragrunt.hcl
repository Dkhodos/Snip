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

inputs = {
  service_name          = "click-worker"
  image                 = "gcr.io/cloudrun/hello"
  memory                = "256Mi"
  min_instances         = 0
  max_instances         = 2
  public                = false
  service_account_email = dependency.project.outputs.cloud_run_service_account_email

  # No VPC needed — click-worker has no database access

  env_vars = {
    ENVIRONMENT        = "staging"
    ANALYTICS_PROVIDER = "gcp_bigquery"
    GCP_PROJECT_ID     = "snip-491719"
    BQ_DATASET         = "snip_analytics_pre_prod"
    BQ_TABLE           = "click_events"
  }
}
