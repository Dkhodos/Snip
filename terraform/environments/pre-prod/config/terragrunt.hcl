include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/config.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock-sa@snip-491719.iam.gserviceaccount.com"
  }
}

dependency "ci_oidc" {
  config_path = "../ci-oidc"

  mock_outputs = {
    ci_service_account_email = "mock-ci-deploy@snip-491719.iam.gserviceaccount.com"
  }
}

inputs = {
  devops_root = "${get_repo_root()}/.devops"
  services    = ["backend", "frontend", "redirect", "click-worker", "migrate"]
  env_enabled    = true
  manage_secrets = true

  cloud_run_service_account_email = dependency.project.outputs.cloud_run_service_account_email
  ci_deploy_service_account_email = dependency.ci_oidc.outputs.ci_service_account_email
}
