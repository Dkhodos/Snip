resource "google_cloud_run_v2_service" "backend" {
  name     = "snip-backend-${var.environment}"
  location = var.region

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # Direct VPC Egress — free alternative to VPC Connector
    vpc_access {
      network_interfaces {
        network    = var.vpc_id
        subnetwork = var.subnet_id
      }
      egress = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      # Environment variables from Secret Manager
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = var.database_url_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "CLERK_PUBLISHABLE_KEY"
        value_source {
          secret_key_ref {
            secret  = var.clerk_publishable_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "CLERK_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.clerk_secret_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "RESEND_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.resend_api_key_secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment == "prod" ? "production" : "staging"
      }

      env {
        name  = "EMAIL_PROVIDER"
        value = var.email_provider
      }

      env {
        name  = "EMAIL_FROM"
        value = var.email_from
      }

      env {
        name  = "CLICK_THRESHOLD"
        value = tostring(var.click_threshold)
      }

      env {
        name  = "ALLOWED_ORIGINS"
        value = var.allowed_origins
      }
    }
  }

  deletion_protection = false

  # Image is managed by CI deploy workflow, not Terraform
  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].containers[0].image,
    ]
  }
}

# Make the service publicly accessible
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.backend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
