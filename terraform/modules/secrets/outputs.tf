output "database_url_secret_id" {
  value = google_secret_manager_secret.secrets["snip-database-url-${var.environment}"].secret_id
}

output "clerk_publishable_secret_id" {
  value = google_secret_manager_secret.secrets["snip-clerk-publishable-${var.environment}"].secret_id
}

output "clerk_secret_secret_id" {
  value = google_secret_manager_secret.secrets["snip-clerk-secret-${var.environment}"].secret_id
}

output "resend_api_key_secret_id" {
  value = google_secret_manager_secret.secrets["snip-resend-api-key-${var.environment}"].secret_id
}

output "redirect_base_url_secret_id" {
  value = google_secret_manager_secret.secrets["snip-redirect-base-url-${var.environment}"].secret_id
}

output "cloudflare_secret_id" {
  value = google_secret_manager_secret.global_secrets["snip-cloudflare-api-token"].secret_id
}
