"""Shared fixtures for telemetry tests."""

import pytest
from opentelemetry import trace
from opentelemetry.metrics import _internal as metrics_internal


@pytest.fixture(autouse=True)
def _reset_otel():
    """Reset global OTel providers so each test starts fresh."""
    yield

    trace._TRACER_PROVIDER_SET_ONCE._done = False  # type: ignore[attr-defined]
    trace._TRACER_PROVIDER = None  # type: ignore[attr-defined]

    metrics_internal._METER_PROVIDER_SET_ONCE._done = False  # type: ignore[attr-defined]
    metrics_internal._METER_PROVIDER = None  # type: ignore[attr-defined]

    for instrumentor_path in [
        "opentelemetry.instrumentation.fastapi.FastAPIInstrumentor",
        "opentelemetry.instrumentation.sqlalchemy.SQLAlchemyInstrumentor",
        "opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor",
        "opentelemetry.instrumentation.grpc.GrpcInstrumentorClient",
    ]:
        try:
            module_path, cls_name = instrumentor_path.rsplit(".", 1)
            mod = __import__(module_path, fromlist=[cls_name])
            instrumentor = getattr(mod, cls_name)()
            if instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.uninstrument()
        except Exception:
            pass
