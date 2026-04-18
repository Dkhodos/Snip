"""Telemetry configuration dataclass."""

from dataclasses import dataclass


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
