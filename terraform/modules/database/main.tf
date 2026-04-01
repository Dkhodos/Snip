# Generate random password for DB user
resource "random_password" "db_password" {
  length  = 24
  special = false
}

# Cloud SQL instance
resource "google_sql_database_instance" "postgres" {
  name             = "snip-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "ZONAL"
    disk_size         = 10
    disk_autoresize   = false

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_id
    }

    backup_configuration {
      enabled = false
    }
  }

  deletion_protection = false

  depends_on = [var.private_vpc_connection]

  lifecycle {
    ignore_changes = [name]
  }
}

# Database
resource "google_sql_database" "shortener" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

# User
resource "google_sql_user" "app_user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}
