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
