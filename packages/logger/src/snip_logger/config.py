"""Logging configuration: call configure_logging() once at app startup."""

import logging

import structlog


def configure_logging(is_local: bool) -> None:
    """Configure structlog and stdlib logging.

    Args:
        is_local: True for human-friendly colored output, False for JSON (production).
    """
    timestamper = structlog.processors.TimeStamper(fmt="%H:%M:%S" if is_local else "iso")

    shared_processors: list[structlog.types.Processor] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
    ]

    try:
        from snip_telemetry.processor import otel_context_processor

        shared_processors.append(otel_context_processor)
    except ImportError:
        pass

    if is_local:
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Wire stdlib logging through structlog so packages using
    # logging.getLogger(__name__) also flow through the same pipeline.
    handler = logging.StreamHandler()
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=shared_processors,
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
