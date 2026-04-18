"""Application configuration."""

from pydantic_settings import BaseSettings
from snip_telemetry import TelemetryConfig


class Settings(BaseSettings):
    database_url: str = ""
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    environment: str = "development"

    # Queue
    queue_provider: str = "dev"
    gcp_project_id: str = ""
    click_topic: str = "click-events"

    # OG image
    og_image_base_url: str = ""
    redirect_base_url: str = ""

    # OpenTelemetry
    otel_enable_fastapi: bool = True
    otel_enable_sqlalchemy: bool = True
    otel_enable_httpx: bool = False
    otel_enable_grpc: bool = True
    otel_exporter_otlp_endpoint: str = ""
    service_version: str = "dev"

    model_config = {"env_file": ".env", "extra": "ignore"}

    def build_telemetry_config(self) -> TelemetryConfig:
        return TelemetryConfig(
            service_name="redirect-service",
            enable_fastapi=self.otel_enable_fastapi,
            enable_sqlalchemy=self.otel_enable_sqlalchemy,
            enable_httpx=self.otel_enable_httpx,
            enable_grpc=self.otel_enable_grpc,
            otlp_endpoint=self.otel_exporter_otlp_endpoint or None,
            service_version=self.service_version,
            environment=self.environment,
        )

    @property
    def effective_database_url(self) -> str:
        """Return DATABASE_URL if set, otherwise construct from individual components."""
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
