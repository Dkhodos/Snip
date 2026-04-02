include "root" {
  path = find_in_parent_folders("root.hcl")
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders("root.hcl"))}/_envcommon/cloudflare-dns.hcl"
  expose = true
}

dependency "cloud_run" {
  config_path = "../cloud-run"

  mock_outputs = {
    service_url = "https://snip-backend-pre-prod-mock-me.a.run.app"
  }
}

dependency "cloud_run_frontend" {
  config_path = "../cloud-run-frontend"

  mock_outputs = {
    service_url = "https://snip-frontend-pre-prod-mock-me.a.run.app"
  }
}

locals {
  backend_origin_host  = trimprefix(dependency.cloud_run.outputs.service_url, "https://")
  frontend_origin_host = trimprefix(dependency.cloud_run_frontend.outputs.service_url, "https://")
}

inputs = {
  cloudflare_zone_id   = "27a72a4ec5db61b37b966524a1012fef"
  domain               = "snip-app.win"
  frontend_origin_host = local.frontend_origin_host
  backend_origin_host  = local.backend_origin_host
}
