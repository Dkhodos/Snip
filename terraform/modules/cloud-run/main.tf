resource "google_cloud_run_v2_service" "this" {
  name     = "snip-${var.service_name}-${var.environment}"
  location = var.region

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

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

      ports {
        container_port = var.container_port
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        cpu_idle = true
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

  deletion_protection = false

  # Image and env vars are managed by CI deploy workflow, not Terraform
  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].containers[0].image,
      scaling,
    ]
  }
}

# Make the service publicly accessible
resource "google_cloud_run_v2_service_iam_member" "public" {
  count    = var.public ? 1 : 0
  name     = google_cloud_run_v2_service.this.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Grant specific service accounts invoker access (e.g. for Pub/Sub push)
resource "google_cloud_run_v2_service_iam_member" "invoker" {
  count    = length(var.invoker_service_accounts)
  name     = google_cloud_run_v2_service.this.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.invoker_service_accounts[count.index]}"
}

# Prune old Cloud Run revisions on every Terraform apply.
# GCP has no native max_revisions API; this best-effort cleanup runs via gcloud.
# It only fires when the service is (re)created or revision_versions_to_keep changes.
resource "null_resource" "prune_revisions" {
  triggers = {
    service_name  = google_cloud_run_v2_service.this.name
    max_revisions = var.revision_versions_to_keep
  }

  provisioner "local-exec" {
    command = <<-EOT
      revisions=$(gcloud run revisions list \
        --service="${google_cloud_run_v2_service.this.name}" \
        --region="${var.region}" \
        --project="${var.project_id}" \
        --sort-by="~metadata.creationTimestamp" \
        --format="value(name)" 2>/dev/null \
        | tail -n +${var.revision_versions_to_keep + 1})
      for rev in $revisions; do
        echo "Pruning old Cloud Run revision: $rev"
        gcloud run revisions delete "$rev" \
          --region="${var.region}" \
          --project="${var.project_id}" \
          --quiet 2>/dev/null || true
      done
    EOT
  }

  depends_on = [google_cloud_run_v2_service.this]
}
