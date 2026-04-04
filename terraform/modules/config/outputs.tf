output "env_vars" {
  description = "Map of service_name → map(string) of plain env vars (UPPER_SNAKE_CASE keys)"
  value       = local.env_vars
}

output "secret_env_vars" {
  description = "Map of service_name → map(string) of env_var_name → secret_id for Cloud Run secret_key_ref"
  value       = local.secret_env_vars
}

output "parameter_ids" {
  description = "Map of service_name → Parameter Manager parameter ID (empty when env_enabled=false)"
  value = {
    for svc in var.services : svc => (
      var.env_enabled
      ? google_parameter_manager_parameter.service_config[svc].id
      : ""
    )
  }
}
