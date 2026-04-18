"""@traced decorator for adding OpenTelemetry spans to functions."""

import functools
import inspect
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar, overload

from opentelemetry import trace
from opentelemetry.trace import StatusCode

P = ParamSpec("P")
R = TypeVar("R")


def _get_tracer() -> trace.Tracer:
    return trace.get_tracer("snip")


@overload
def traced(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]: ...


@overload
def traced(func: Callable[P, R]) -> Callable[P, R]: ...


def traced(func: Callable[P, R]) -> Callable[P, R]:  # type: ignore[misc]
    span_name = func.__qualname__

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with _get_tracer().start_as_current_span(span_name) as span:
                try:
                    return await func(*args, **kwargs)  # type: ignore[misc]
                except Exception as exc:
                    span.set_status(StatusCode.ERROR, str(exc))
                    span.record_exception(exc)
                    raise

        return async_wrapper  # type: ignore[return-value]

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with _get_tracer().start_as_current_span(span_name) as span:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                span.set_status(StatusCode.ERROR, str(exc))
                span.record_exception(exc)
                raise

    return sync_wrapper  # type: ignore[return-value]
