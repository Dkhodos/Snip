"""OpenTelemetry setup: call init_telemetry() once at app startup."""

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.resource import ResourceAttributes

from snip_telemetry.config import TelemetryConfig


def init_telemetry(config: TelemetryConfig) -> None:
    """Configure OpenTelemetry tracing, metrics, and auto-instrumentation.

    Call before configure_logging() in the app lifespan so that the structlog
    processor can read trace context from an already-active TracerProvider.
    """
    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: config.service_name,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: config.environment,
            ResourceAttributes.SERVICE_VERSION: config.service_version,
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    meter_provider = MeterProvider(resource=resource)

    if config.otlp_endpoint:
        _attach_otlp_exporters(tracer_provider, meter_provider)

    trace.set_tracer_provider(tracer_provider)
    metrics.set_meter_provider(meter_provider)

    _instrument(config)


def _attach_otlp_exporters(tracer_provider: TracerProvider, meter_provider: MeterProvider) -> None:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    meter_provider._all_metric_readers.add(  # type: ignore[attr-defined]
        PeriodicExportingMetricReader(OTLPMetricExporter())
    )


def _instrument(config: TelemetryConfig) -> None:
    if config.enable_fastapi:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor().instrument()

    if config.enable_sqlalchemy:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument()

    if config.enable_httpx:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()

    if config.enable_grpc:
        from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient

        GrpcInstrumentorClient().instrument()
