# Prod is disabled — remove skip = true when ready to deploy
skip = true

include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/ci-oidc.hcl"
  expose = true
}
