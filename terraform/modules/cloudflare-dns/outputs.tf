output "frontend_url" {
  value = "https://${local.frontend_fqdn}"
}

output "backend_url" {
  value = "https://${local.backend_fqdn}"
}
