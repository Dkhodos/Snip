"""Tests for @traced decorator."""

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode, set_tracer_provider

from snip_telemetry.decorator import traced


@pytest.fixture()
def span_exporter():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    set_tracer_provider(provider)
    yield exporter
    exporter.shutdown()


class TestTracedAsync:
    async def test_returns_value(self, span_exporter: InMemorySpanExporter) -> None:
        @traced
        async def add(a: int, b: int) -> int:
            return a + b

        result = await add(1, 2)
        assert result == 3

    async def test_creates_span(self, span_exporter: InMemorySpanExporter) -> None:
        @traced
        async def my_func() -> None:
            pass

        await my_func()
        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].name == "TestTracedAsync.test_creates_span.<locals>.my_func"

    async def test_records_exception(self, span_exporter: InMemorySpanExporter) -> None:
        @traced
        async def failing() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            await failing()

        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].status.status_code == StatusCode.ERROR
        events = spans[0].events
        assert any(e.name == "exception" for e in events)

    async def test_preserves_metadata(self) -> None:
        @traced
        async def documented_func() -> None:
            """Docstring."""

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "Docstring."


class TestTracedSync:
    def test_returns_value(self, span_exporter: InMemorySpanExporter) -> None:
        @traced
        def multiply(a: int, b: int) -> int:
            return a * b

        result = multiply(3, 4)
        assert result == 12

    def test_creates_span(self, span_exporter: InMemorySpanExporter) -> None:
        @traced
        def sync_func() -> None:
            pass

        sync_func()
        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].name == "TestTracedSync.test_creates_span.<locals>.sync_func"

    def test_records_exception(self, span_exporter: InMemorySpanExporter) -> None:
        @traced
        def failing() -> None:
            raise RuntimeError("sync boom")

        with pytest.raises(RuntimeError, match="sync boom"):
            failing()

        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].status.status_code == StatusCode.ERROR
