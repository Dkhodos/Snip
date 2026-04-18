"""Telemetry configuration dataclass."""

import os
from dataclasses import dataclass


def _env_bool(key: str) -> bool:
    return os.environ.get(key, "").lower() in ("true", "1", "yes")


@dataclass(frozen=True)
class TelemetryConfig:
    service_name: str
    enable_fastapi: bool = False
    enable_sqlalchemy: bool = False
    enable_httpx: bool = False
    enable_grpc: bool = False
    otlp_endpoint: str | None = None
    service_version: str = "dev"
    environment: str = "development"

    @classmethod
    def from_env(cls) -> "TelemetryConfig":
        service_name = os.environ.get("OTEL_SERVICE_NAME", "")
        if not service_name:
            raise ValueError("OTEL_SERVICE_NAME environment variable is required")

        return cls(
            service_name=service_name,
            enable_fastapi=_env_bool("OTEL_ENABLE_FASTAPI"),
            enable_sqlalchemy=_env_bool("OTEL_ENABLE_SQLALCHEMY"),
            enable_httpx=_env_bool("OTEL_ENABLE_HTTPX"),
            enable_grpc=_env_bool("OTEL_ENABLE_GRPC"),
            otlp_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or None,
            service_version=os.environ.get("SERVICE_VERSION", "dev"),
            environment=os.environ.get("ENVIRONMENT", "development"),
        )
