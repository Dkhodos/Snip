"""Tests for init_telemetry()."""

from unittest.mock import MagicMock, patch

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from snip_telemetry.init import init_telemetry


class TestInitTelemetry:
    def test_sets_tracer_provider(self) -> None:
        init_telemetry("test-svc", is_local=True)
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)

    def test_resource_has_service_name(self) -> None:
        init_telemetry("my-service", is_local=True)
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        attrs = dict(provider.resource.attributes)
        assert attrs["service.name"] == "my-service"

    def test_resource_development_environment(self) -> None:
        init_telemetry("svc", is_local=True)
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        attrs = dict(provider.resource.attributes)
        assert attrs["deployment.environment"] == "development"

    def test_resource_production_environment(self) -> None:
        init_telemetry("svc", is_local=False)
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        attrs = dict(provider.resource.attributes)
        assert attrs["deployment.environment"] == "production"

    def test_resource_service_version_default(self) -> None:
        init_telemetry("svc", is_local=True)
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        attrs = dict(provider.resource.attributes)
        assert attrs["service.version"] == "dev"

    def test_resource_service_version_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SERVICE_VERSION", "1.2.3")
        init_telemetry("svc", is_local=True)
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        attrs = dict(provider.resource.attributes)
        assert attrs["service.version"] == "1.2.3"

    def test_no_exporter_without_endpoint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
        init_telemetry("svc", is_local=True)
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        processors = provider._active_span_processor._span_processors  # type: ignore[attr-defined]
        assert len(processors) == 0

    @patch("snip_telemetry.init._attach_otlp_exporters")
    def test_attaches_exporter_with_endpoint(
        self, mock_attach: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        init_telemetry("svc", is_local=True)
        mock_attach.assert_called_once()

    @patch("snip_telemetry.init._instrument")
    def test_calls_instrument(self, mock_instrument: MagicMock) -> None:
        init_telemetry("svc", is_local=True)
        mock_instrument.assert_called_once()


class TestInstrument:
    @patch("opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor.instrument")
    @patch("opentelemetry.instrumentation.sqlalchemy.SQLAlchemyInstrumentor.instrument")
    @patch("opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument")
    def test_instruments_all_libraries(
        self,
        mock_fastapi: MagicMock,
        mock_sqlalchemy: MagicMock,
        mock_httpx: MagicMock,
    ) -> None:
        from snip_telemetry.init import _instrument

        _instrument()
        mock_fastapi.assert_called_once()
        mock_sqlalchemy.assert_called_once()
        mock_httpx.assert_called_once()
