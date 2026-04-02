"""Factory for bound loggers."""

from typing import Optional

import structlog


def get_logger(
    app_name: str,
    log_prefix: Optional[str] = None,
) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound with app context.

    Args:
        app_name: Identifies the application or service in log output.
        log_prefix: Optional sub-scope (e.g. feature name) bound as ``prefix``.
    """
    logger = structlog.get_logger().bind(app=app_name)
    if log_prefix is not None:
        logger = logger.bind(prefix=log_prefix)
    return logger  # type: ignore[return-value]
