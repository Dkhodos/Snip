output "click_events_topic_name" {
  value = google_pubsub_topic.click_events.name
}

output "click_events_topic_id" {
  value = google_pubsub_topic.click_events.id
}

output "dlq_topic_name" {
  value = google_pubsub_topic.click_events_dlq.name
}
