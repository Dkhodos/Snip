"""Tests for otel_context_processor."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags

from snip_telemetry.processor import otel_context_processor


class TestOtelContextProcessor:
    def test_no_active_span(self) -> None:
        event_dict: dict = {"event": "test"}
        result = otel_context_processor(None, "info", event_dict)
        assert "trace_id" not in result
        assert "span_id" not in result

    def test_active_span_injects_ids(self) -> None:
        provider = TracerProvider()
        tracer = provider.get_tracer("test")
        with tracer.start_as_current_span("test-span"):
            event_dict: dict = {"event": "test"}
            result = otel_context_processor(None, "info", event_dict)
            assert "trace_id" in result
            assert "span_id" in result
            assert len(result["trace_id"]) == 32
            assert len(result["span_id"]) == 16

    def test_preserves_existing_keys(self) -> None:
        provider = TracerProvider()
        tracer = provider.get_tracer("test")
        with tracer.start_as_current_span("test-span"):
            event_dict: dict = {"event": "test", "custom_key": "value"}
            result = otel_context_processor(None, "info", event_dict)
            assert result["custom_key"] == "value"
            assert result["event"] == "test"

    def test_invalid_span_context_skipped(self) -> None:
        ctx = SpanContext(trace_id=0, span_id=0, is_remote=False, trace_flags=TraceFlags(0))
        span = NonRecordingSpan(ctx)
        token = trace.context_api.attach(trace.set_span_in_context(span))
        try:
            event_dict: dict = {"event": "test"}
            result = otel_context_processor(None, "info", event_dict)
            assert "trace_id" not in result
            assert "span_id" not in result
        finally:
            trace.context_api.detach(token)
