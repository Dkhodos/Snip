include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/secrets.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    cloud_run_service_account_email = "mock-sa@snip-491719.iam.gserviceaccount.com"
  }
}

dependency "database" {
  config_path = "../database"

  mock_outputs = {
    database_url = "postgresql+asyncpg://mock:mock@127.0.0.1:5432/mock"
  }
}

# Clerk/Resend keys — pass via TF_VAR_ env vars (NEVER commit)
inputs = {
  cloud_run_service_account_email = dependency.project.outputs.cloud_run_service_account_email
  database_url                    = dependency.database.outputs.database_url
  clerk_publishable_key           = ""
  clerk_secret_key                = ""
  resend_api_key                  = ""
}
