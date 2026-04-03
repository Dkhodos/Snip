output "dataset_id" {
  value = google_bigquery_dataset.analytics.dataset_id
}

output "table_id" {
  value = google_bigquery_table.click_events.table_id
}

output "full_table_id" {
  value = "${var.project_id}.${google_bigquery_dataset.analytics.dataset_id}.${google_bigquery_table.click_events.table_id}"
}
