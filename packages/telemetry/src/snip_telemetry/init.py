"""OpenTelemetry setup: call init_telemetry() once at app startup."""

import os

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.resource import ResourceAttributes


def init_telemetry(service_name: str, *, is_local: bool) -> None:
    """Configure OpenTelemetry tracing, metrics, and auto-instrumentation.

    Call before configure_logging() in the app lifespan so that the structlog
    processor can read trace context from an already-active TracerProvider.
    """
    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: (
                "development" if is_local else "production"
            ),
            ResourceAttributes.SERVICE_VERSION: os.environ.get("SERVICE_VERSION", "dev"),
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    meter_provider = MeterProvider(resource=resource)

    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        _attach_otlp_exporters(tracer_provider, meter_provider)

    trace.set_tracer_provider(tracer_provider)
    metrics.set_meter_provider(meter_provider)

    _instrument()


def _attach_otlp_exporters(tracer_provider: TracerProvider, meter_provider: MeterProvider) -> None:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    meter_provider._all_metric_readers.add(  # type: ignore[attr-defined]
        PeriodicExportingMetricReader(OTLPMetricExporter())
    )


def _instrument() -> None:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()

    try:
        from opentelemetry.instrumentation.grpc import (
            GrpcInstrumentorClient,  # type: ignore[import-not-found]
        )

        GrpcInstrumentorClient().instrument()
    except ImportError:
        pass
