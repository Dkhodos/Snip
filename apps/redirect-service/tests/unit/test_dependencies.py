"""Tests for dependency injection wiring."""

from unittest.mock import AsyncMock, MagicMock, patch

from redirect_service.dependencies import get_link_store, get_queue_publisher, get_redirect_manager


class TestDependencies:
    @patch("redirect_service.dependencies.create_queue_publisher")
    def test_get_queue_publisher_creates_singleton(self, mock_create: MagicMock) -> None:
        import redirect_service.dependencies as deps

        deps._publisher = None
        mock_create.return_value = MagicMock()

        pub1 = get_queue_publisher()
        pub2 = get_queue_publisher()

        assert pub1 is pub2
        mock_create.assert_called_once()
        deps._publisher = None  # reset for other tests

    def test_get_link_store(self) -> None:
        session = AsyncMock()
        store = get_link_store(session=session)
        assert store is not None

    def test_get_redirect_manager(self) -> None:
        link_store = MagicMock()
        publisher = MagicMock()
        manager = get_redirect_manager(link_store=link_store, publisher=publisher)
        assert manager is not None
