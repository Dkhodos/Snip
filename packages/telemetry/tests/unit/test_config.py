"""Tests for TelemetryConfig."""

import pytest

from snip_telemetry.config import TelemetryConfig


class TestTelemetryConfig:
    def test_defaults(self) -> None:
        config = TelemetryConfig(service_name="test")
        assert config.service_name == "test"
        assert config.enable_fastapi is False
        assert config.enable_sqlalchemy is False
        assert config.enable_httpx is False
        assert config.enable_grpc is False
        assert config.otlp_endpoint is None
        assert config.service_version == "dev"
        assert config.environment == "development"

    def test_explicit_values(self) -> None:
        config = TelemetryConfig(
            service_name="my-svc",
            enable_fastapi=True,
            enable_grpc=True,
            otlp_endpoint="http://localhost:4317",
            service_version="1.0.0",
            environment="staging",
        )
        assert config.service_name == "my-svc"
        assert config.enable_fastapi is True
        assert config.enable_sqlalchemy is False
        assert config.enable_grpc is True
        assert config.otlp_endpoint == "http://localhost:4317"
        assert config.service_version == "1.0.0"
        assert config.environment == "staging"

    def test_frozen(self) -> None:
        config = TelemetryConfig(service_name="test")
        with pytest.raises(AttributeError):
            config.service_name = "other"  # type: ignore[misc]


class TestFromEnv:
    def test_raises_without_service_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OTEL_SERVICE_NAME", raising=False)
        with pytest.raises(ValueError, match="OTEL_SERVICE_NAME"):
            TelemetryConfig.from_env()

    def test_defaults_when_only_service_name_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OTEL_SERVICE_NAME", "my-svc")
        for key in [
            "OTEL_ENABLE_FASTAPI",
            "OTEL_ENABLE_SQLALCHEMY",
            "OTEL_ENABLE_HTTPX",
            "OTEL_ENABLE_GRPC",
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "SERVICE_VERSION",
            "ENVIRONMENT",
        ]:
            monkeypatch.delenv(key, raising=False)

        config = TelemetryConfig.from_env()
        assert config.service_name == "my-svc"
        assert config.enable_fastapi is False
        assert config.enable_sqlalchemy is False
        assert config.enable_httpx is False
        assert config.enable_grpc is False
        assert config.otlp_endpoint is None
        assert config.service_version == "dev"
        assert config.environment == "development"

    def test_reads_all_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OTEL_SERVICE_NAME", "svc")
        monkeypatch.setenv("OTEL_ENABLE_FASTAPI", "true")
        monkeypatch.setenv("OTEL_ENABLE_SQLALCHEMY", "false")
        monkeypatch.setenv("OTEL_ENABLE_HTTPX", "1")
        monkeypatch.setenv("OTEL_ENABLE_GRPC", "yes")
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4317")
        monkeypatch.setenv("SERVICE_VERSION", "2.0.0")
        monkeypatch.setenv("ENVIRONMENT", "staging")

        config = TelemetryConfig.from_env()
        assert config.enable_fastapi is True
        assert config.enable_sqlalchemy is False
        assert config.enable_httpx is True
        assert config.enable_grpc is True
        assert config.otlp_endpoint == "http://collector:4317"
        assert config.service_version == "2.0.0"
        assert config.environment == "staging"

    def test_empty_endpoint_becomes_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OTEL_SERVICE_NAME", "svc")
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        config = TelemetryConfig.from_env()
        assert config.otlp_endpoint is None
