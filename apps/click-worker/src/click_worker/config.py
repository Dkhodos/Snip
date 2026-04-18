"""Application configuration."""

from pydantic_settings import BaseSettings
from snip_telemetry import TelemetryConfig


class Settings(BaseSettings):
    environment: str = "development"

    # Analytics
    analytics_provider: str = "dev"
    gcp_project_id: str = ""
    bq_dataset: str = ""
    bq_table: str = "click_events"

    # Pub/Sub push authentication
    # Set to the full HTTPS URL of the /ingest endpoint (the push subscription audience).
    # Leave empty to disable verification (dev/test only).
    pubsub_audience: str = ""
    enable_pubsub_auth: bool = True

    # OpenTelemetry
    otel_enable_fastapi: bool = True
    otel_enable_sqlalchemy: bool = False
    otel_enable_httpx: bool = True
    otel_enable_grpc: bool = True
    otel_exporter_otlp_endpoint: str = ""
    service_version: str = "dev"

    model_config = {"env_file": ".env", "extra": "ignore"}

    def build_telemetry_config(self) -> TelemetryConfig:
        return TelemetryConfig(
            service_name="click-worker",
            enable_fastapi=self.otel_enable_fastapi,
            enable_sqlalchemy=self.otel_enable_sqlalchemy,
            enable_httpx=self.otel_enable_httpx,
            enable_grpc=self.otel_enable_grpc,
            otlp_endpoint=self.otel_exporter_otlp_endpoint or None,
            service_version=self.service_version,
            environment=self.environment,
        )


settings = Settings()
