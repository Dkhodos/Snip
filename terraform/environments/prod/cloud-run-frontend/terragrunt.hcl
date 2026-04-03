# Prod is disabled — remove skip = true when ready to deploy
skip = true

include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/cloud-run-frontend.hcl"
  expose = true
}

inputs = {
  service_name = "frontend"
  image        = "gcr.io/cloudrun/hello"
  memory       = "256Mi"
}
