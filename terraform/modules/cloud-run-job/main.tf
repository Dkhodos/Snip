resource "google_cloud_run_v2_job" "this" {
  name     = "snip-${var.job_name}-${var.environment}"
  location = var.region

  template {
    template {
      service_account = var.service_account_email

      # Direct VPC Egress — only when VPC config is provided
      dynamic "vpc_access" {
        for_each = var.vpc_id != null ? [1] : []
        content {
          network_interfaces {
            network    = var.vpc_id
            subnetwork = var.subnet_id
          }
          egress = "PRIVATE_RANGES_ONLY"
        }
      }

      containers {
        image = var.image

        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }

        # Plain environment variables
        dynamic "env" {
          for_each = var.env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        # Secret Manager environment variables
        dynamic "env" {
          for_each = var.secret_env_vars
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value
                version = "latest"
              }
            }
          }
        }
      }
    }
  }

  deletion_protection = false

  # Image is managed by CI migrate workflow, not Terraform
  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].template[0].containers[0].image,
    ]
  }
}
