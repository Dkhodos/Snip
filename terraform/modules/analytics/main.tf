resource "google_bigquery_dataset" "analytics" {
  dataset_id = "snip_analytics_${replace(var.environment, "-", "_")}"
  location   = var.region

  description = "Snip click analytics (${var.environment})"

  default_table_expiration_ms = null
}

resource "google_bigquery_table" "click_events" {
  dataset_id          = google_bigquery_dataset.analytics.dataset_id
  table_id            = "click_events"
  deletion_protection = true

  time_partitioning {
    type  = "DAY"
    field = "clicked_at"
  }

  clustering = ["org_id", "link_id"]

  schema = jsonencode([
    { name = "event_id",    type = "STRING",    mode = "REQUIRED" },
    { name = "link_id",     type = "STRING",    mode = "REQUIRED" },
    { name = "short_code",  type = "STRING",    mode = "REQUIRED" },
    { name = "org_id",      type = "STRING",    mode = "REQUIRED" },
    { name = "clicked_at",  type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "user_agent",  type = "STRING",    mode = "NULLABLE" },
    { name = "country",     type = "STRING",    mode = "NULLABLE" },
    { name = "ingested_at", type = "TIMESTAMP", mode = "REQUIRED" },
  ])
}

# Cloud Run SA: write access (for click worker inserts)
resource "google_bigquery_dataset_iam_member" "editor" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.cloud_run_service_account_email}"
}

# Cloud Run SA: read access (for dashboard backend queries)
resource "google_bigquery_dataset_iam_member" "viewer" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${var.cloud_run_service_account_email}"
}

# Cloud Run SA needs bigquery.jobs.create to run queries
resource "google_project_iam_member" "bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${var.cloud_run_service_account_email}"
}
