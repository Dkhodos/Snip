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

dependency "networking" {
  config_path = "../networking"

  mock_outputs = {
    vpc_id    = "projects/snip-491719/global/networks/snip-vpc-pre-prod"
    subnet_id = "projects/snip-491719/regions/me-west1/subnetworks/snip-subnet-pre-prod"
  }
}

dependency "config" {
  config_path = "../config"

  mock_outputs = {
    env_vars = {
      redirect = {
        ENVIRONMENT    = "staging"
        QUEUE_PROVIDER = "gcp_pubsub"
        CLICK_TOPIC    = "click-events-pre-prod"
      }
    }
    secret_env_vars = {
      redirect = {
        DATABASE_URL = "mock-db-url"
      }
    }
  }
}

dependency "queue" {
  config_path = "../queue"

  mock_outputs = {
    click_events_topic_id = "projects/snip-491719/topics/click-events-pre-prod"
  }
}

inputs = {
  service_name          = "redirect"
  image                 = "gcr.io/cloudrun/hello"
  memory                = "512Mi"
  min_instances         = 0
  max_instances         = 2
  service_account_email = dependency.project.outputs.cloud_run_service_account_email
  vpc_id                = dependency.networking.outputs.vpc_id
  subnet_id             = dependency.networking.outputs.subnet_id

  env_vars        = dependency.config.outputs.env_vars["redirect"]
  secret_env_vars = dependency.config.outputs.secret_env_vars["redirect"]
}
