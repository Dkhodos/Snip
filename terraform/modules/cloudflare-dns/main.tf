# Cloudflare DNS records and Cloud Run domain mappings.

locals {
  frontend_subdomain = "app.${var.environment}"
  backend_subdomain  = "api.${var.environment}"
  redirect_subdomain = "r.${var.environment}"
  frontend_fqdn      = "${local.frontend_subdomain}.${var.domain}"
  backend_fqdn       = "${local.backend_subdomain}.${var.domain}"
  redirect_fqdn      = "${local.redirect_subdomain}.${var.domain}"
}

# --- Cloudflare DNS Records (grey cloud — Google handles TLS) ---

resource "cloudflare_dns_record" "frontend" {
  zone_id = var.cloudflare_zone_id
  name    = local.frontend_subdomain
  type    = "CNAME"
  content = "ghs.googlehosted.com"
  proxied = false
  ttl     = 300
}

resource "cloudflare_dns_record" "backend" {
  zone_id = var.cloudflare_zone_id
  name    = local.backend_subdomain
  type    = "CNAME"
  content = "ghs.googlehosted.com"
  proxied = false
  ttl     = 300
}

# --- Cloud Run Domain Mappings ---

resource "google_cloud_run_domain_mapping" "frontend" {
  location = var.region
  name     = local.frontend_fqdn

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = var.frontend_service_name
  }
}

resource "google_cloud_run_domain_mapping" "backend" {
  location = var.region
  name     = local.backend_fqdn

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = var.backend_service_name
  }
}

# --- Redirect service (r.{env}.snip-app.win) ---

resource "cloudflare_dns_record" "redirect" {
  count   = var.redirect_service_name != null ? 1 : 0
  zone_id = var.cloudflare_zone_id
  name    = local.redirect_subdomain
  type    = "CNAME"
  content = "ghs.googlehosted.com"
  proxied = false
  ttl     = 300
}

resource "google_cloud_run_domain_mapping" "redirect" {
  count    = var.redirect_service_name != null ? 1 : 0
  location = var.region
  name     = local.redirect_fqdn

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = var.redirect_service_name
  }
}
