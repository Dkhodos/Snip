include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/database.hcl"
  expose = true
}

dependency "networking" {
  config_path = "../networking"

  mock_outputs = {
    vpc_id                 = "projects/snip-491719/global/networks/snip-vpc-pre-prod"
    private_vpc_connection = "mock-connection"
  }
}

inputs = {
  db_tier                = "db-f1-micro"
  vpc_id                 = dependency.networking.outputs.vpc_id
  private_vpc_connection = dependency.networking.outputs.private_vpc_connection
}
