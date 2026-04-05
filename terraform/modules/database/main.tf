# Cloud SQL PostgreSQL instance with private VPC networking.

# Generate random password for DB user
resource "random_password" "db_password" {
  length  = 24
  special = false
}

# Cloud SQL instance
resource "google_sql_database_instance" "postgres" {
  name             = "snip-db-${var.environment}-${var.region}"
  database_version = "POSTGRES_17"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "ZONAL"
    disk_size         = 10
    disk_autoresize   = false

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_id
      ssl_mode        = "ENCRYPTED_ONLY"
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    database_flags {
      name  = "log_hostname"
      value = "on"
    }
    database_flags {
      name  = "log_min_error_statement"
      value = "error"
    }
    database_flags {
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }
    database_flags {
      name  = "log_statement"
      value = "all"
    }
    database_flags {
      name  = "log_duration"
      value = "on"
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
