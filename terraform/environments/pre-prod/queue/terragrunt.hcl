include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/queue.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock-sa@snip-491719.iam.gserviceaccount.com"
    project_number                  = "123456789"
  }
}

inputs = {
  project_number                  = dependency.project.outputs.project_number
  cloud_run_service_account_email = dependency.project.outputs.cloud_run_service_account_email
  # Push subscription will be configured after click-worker is deployed
  click_worker_endpoint           = ""
  push_service_account_email      = ""
}
