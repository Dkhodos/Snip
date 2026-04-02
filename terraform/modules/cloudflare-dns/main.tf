locals {
  frontend_subdomain = "app.${var.environment}"
  backend_subdomain  = "api.${var.environment}"
  frontend_fqdn      = "${local.frontend_subdomain}.${var.domain}"
  backend_fqdn       = "${local.backend_subdomain}.${var.domain}"
}

# --- DNS Records ---

resource "cloudflare_dns_record" "frontend" {
  zone_id = var.cloudflare_zone_id
  name    = local.frontend_subdomain
  type    = "CNAME"
  content = var.frontend_origin_host
  proxied = true
  ttl     = 1
}

resource "cloudflare_dns_record" "backend" {
  zone_id = var.cloudflare_zone_id
  name    = local.backend_subdomain
  type    = "CNAME"
  content = var.backend_origin_host
  proxied = true
  ttl     = 1
}

# --- Origin Rules (rewrite Host header so Cloud Run routes correctly) ---

resource "cloudflare_ruleset" "origin_rules" {
  zone_id     = var.cloudflare_zone_id
  name        = "Cloud Run origin rules (${var.environment})"
  description = "Rewrite Host header for Cloud Run services"
  kind        = "zone"
  phase       = "http_request_origin"

  rules = [
    {
      action      = "route"
      description = "Frontend: ${local.frontend_fqdn} -> ${var.frontend_origin_host}"
      enabled     = true
      expression  = "(http.host eq \"${local.frontend_fqdn}\")"
      action_parameters = {
        host_header = var.frontend_origin_host
      }
    },
    {
      action      = "route"
      description = "Backend: ${local.backend_fqdn} -> ${var.backend_origin_host}"
      enabled     = true
      expression  = "(http.host eq \"${local.backend_fqdn}\")"
      action_parameters = {
        host_header = var.backend_origin_host
      }
    },
  ]
}
