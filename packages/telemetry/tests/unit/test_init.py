"""Tests for init_telemetry()."""

from unittest.mock import MagicMock, patch

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from snip_telemetry.config import TelemetryConfig
from snip_telemetry.init import init_telemetry


def _config(**overrides: object) -> TelemetryConfig:
    defaults: dict = {"service_name": "test-svc"}
    defaults.update(overrides)
    return TelemetryConfig(**defaults)  # type: ignore[arg-type]


class TestInitTelemetry:
    def test_sets_tracer_provider(self) -> None:
        init_telemetry(_config())
        assert isinstance(trace.get_tracer_provider(), TracerProvider)

    def test_resource_has_service_name(self) -> None:
        init_telemetry(_config(service_name="my-service"))
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        assert dict(provider.resource.attributes)["service.name"] == "my-service"

    def test_resource_environment(self) -> None:
        init_telemetry(_config(environment="staging"))
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        assert dict(provider.resource.attributes)["deployment.environment"] == "staging"

    def test_resource_environment_default(self) -> None:
        init_telemetry(_config())
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        assert dict(provider.resource.attributes)["deployment.environment"] == "development"

    def test_resource_service_version(self) -> None:
        init_telemetry(_config(service_version="1.2.3"))
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        assert dict(provider.resource.attributes)["service.version"] == "1.2.3"

    def test_resource_service_version_default(self) -> None:
        init_telemetry(_config())
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        assert dict(provider.resource.attributes)["service.version"] == "dev"

    def test_no_exporter_without_endpoint(self) -> None:
        init_telemetry(_config(otlp_endpoint=None))
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        processors = provider._active_span_processor._span_processors  # type: ignore[attr-defined]
        assert len(processors) == 0

    @patch("snip_telemetry.init._attach_otlp_exporters")
    def test_attaches_exporter_with_endpoint(self, mock_attach: MagicMock) -> None:
        init_telemetry(_config(otlp_endpoint="http://localhost:4317"))
        mock_attach.assert_called_once()

    @patch("snip_telemetry.init._instrument")
    def test_calls_instrument_with_config(self, mock_instrument: MagicMock) -> None:
        cfg = _config(enable_fastapi=True)
        init_telemetry(cfg)
        mock_instrument.assert_called_once_with(cfg)


class TestInstrument:
    @patch("opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument")
    def test_instruments_only_fastapi(self, mock_fastapi: MagicMock) -> None:
        init_telemetry(_config(enable_fastapi=True))
        mock_fastapi.assert_called_once()

    @patch("opentelemetry.instrumentation.sqlalchemy.SQLAlchemyInstrumentor.instrument")
    def test_instruments_only_sqlalchemy(self, mock_sqlalchemy: MagicMock) -> None:
        init_telemetry(_config(enable_sqlalchemy=True))
        mock_sqlalchemy.assert_called_once()

    @patch("opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor.instrument")
    def test_instruments_only_httpx(self, mock_httpx: MagicMock) -> None:
        init_telemetry(_config(enable_httpx=True))
        mock_httpx.assert_called_once()

    @patch("opentelemetry.instrumentation.grpc.GrpcInstrumentorClient.instrument")
    def test_instruments_only_grpc(self, mock_grpc: MagicMock) -> None:
        init_telemetry(_config(enable_grpc=True))
        mock_grpc.assert_called_once()

    @patch("opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor.instrument")
    @patch("opentelemetry.instrumentation.sqlalchemy.SQLAlchemyInstrumentor.instrument")
    @patch("opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument")
    def test_instruments_nothing_by_default(
        self,
        mock_fastapi: MagicMock,
        mock_sqlalchemy: MagicMock,
        mock_httpx: MagicMock,
    ) -> None:
        init_telemetry(_config())
        mock_fastapi.assert_not_called()
        mock_sqlalchemy.assert_not_called()
        mock_httpx.assert_not_called()

    @patch("opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor.instrument")
    @patch("opentelemetry.instrumentation.sqlalchemy.SQLAlchemyInstrumentor.instrument")
    @patch("opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument")
    def test_instruments_multiple(
        self,
        mock_fastapi: MagicMock,
        mock_sqlalchemy: MagicMock,
        mock_httpx: MagicMock,
    ) -> None:
        init_telemetry(_config(enable_fastapi=True, enable_httpx=True))
        mock_fastapi.assert_called_once()
        mock_sqlalchemy.assert_not_called()
        mock_httpx.assert_called_once()
