include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/networking.hcl"
  expose = true
}

dependency "project" {
  config_path = "../project"

  mock_outputs = {
    api_services = []
  }
}
