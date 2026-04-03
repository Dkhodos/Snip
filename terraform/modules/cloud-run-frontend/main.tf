resource "google_cloud_run_v2_service" "frontend" {
  name     = "snip-frontend-${var.environment}"
  location = var.region

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # No VPC access — nginx proxies /api to the backend and serves static files
    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      env {
        name  = "BACKEND_URL"
        value = var.backend_url
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
        cpu_idle = true
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
      template[0].containers[0].env,
      scaling,
    ]
  }
}

# Public access
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.frontend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
