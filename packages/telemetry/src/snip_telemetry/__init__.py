"""snip-telemetry: OpenTelemetry setup for Snip services."""

from snip_telemetry.decorator import traced
from snip_telemetry.init import init_telemetry
from snip_telemetry.processor import otel_context_processor

__all__ = [
    "init_telemetry",
    "otel_context_processor",
    "traced",
]
