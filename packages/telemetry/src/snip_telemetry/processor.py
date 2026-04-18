"""Structlog processor that injects OpenTelemetry trace context into log events."""

from collections.abc import MutableMapping
from typing import Any

from opentelemetry import trace


def otel_context_processor(
    logger: Any, method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Add trace_id and span_id from the current OTel span to the log event."""
    ctx = trace.get_current_span().get_span_context()
    if ctx.trace_id != 0:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict
