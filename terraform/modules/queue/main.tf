# Click events topic
resource "google_pubsub_topic" "click_events" {
  name = "click-events-${var.environment}"
}

# Dead letter topic
resource "google_pubsub_topic" "click_events_dlq" {
  name = "click-events-dlq-${var.environment}"
}

# Push subscription to the click worker Cloud Run service
resource "google_pubsub_subscription" "click_events_push" {
  name  = "click-events-push-${var.environment}"
  topic = google_pubsub_topic.click_events.id

  ack_deadline_seconds = 30

  push_config {
    push_endpoint = var.click_worker_endpoint

    oidc_token {
      service_account_email = var.push_service_account_email
    }
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.click_events_dlq.id
    max_delivery_attempts = 5
  }

  # Don't create the push subscription until the worker endpoint is configured
  count = var.click_worker_endpoint != "" ? 1 : 0
}

# Pull subscription on DLQ for manual inspection
resource "google_pubsub_subscription" "click_events_dlq_pull" {
  name  = "click-events-dlq-pull-${var.environment}"
  topic = google_pubsub_topic.click_events_dlq.id

  ack_deadline_seconds       = 60
  message_retention_duration = "604800s" # 7 days
}

# Cloud Run SA can publish to the click events topic
resource "google_pubsub_topic_iam_member" "publisher" {
  topic  = google_pubsub_topic.click_events.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${var.cloud_run_service_account_email}"
}

# Pub/Sub service agent can publish to DLQ (for dead-lettering)
resource "google_pubsub_topic_iam_member" "dlq_publisher" {
  topic  = google_pubsub_topic.click_events_dlq.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

# Pub/Sub service agent can subscribe (needed for dead letter forwarding)
resource "google_pubsub_subscription_iam_member" "dlq_subscriber" {
  count        = var.click_worker_endpoint != "" ? 1 : 0
  subscription = google_pubsub_subscription.click_events_push[0].id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}
