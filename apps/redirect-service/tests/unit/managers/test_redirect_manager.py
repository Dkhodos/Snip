"""Tests for the redirect manager."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from redirect_service.exceptions import LinkExpiredError, LinkNotFoundError
from redirect_service.managers.redirect_manager import RedirectManager


def _make_link(
    *,
    target_url: str = "https://example.com",
    short_code: str = "abc123",
    click_count: int = 0,
    expires_at: datetime | None = None,
    org_id: str = "org-1",
    created_by: str | None = "user-1",
) -> MagicMock:
    link = MagicMock()
    link.id = "link-1"
    link.target_url = target_url
    link.short_code = short_code
    link.click_count = click_count
    link.expires_at = expires_at
    link.org_id = org_id
    link.created_by = created_by
    return link


class TestRedirectManager:
    @pytest.fixture()
    def link_store(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture()
    def publisher(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture()
    def manager(self, link_store: AsyncMock, publisher: AsyncMock) -> RedirectManager:
        return RedirectManager(
            link_store=link_store,
            publisher=publisher,
            click_topic="click-events",
        )

    async def test_resolve_redirect_happy_path(
        self, manager: RedirectManager, link_store: AsyncMock, publisher: AsyncMock
    ) -> None:
        link = _make_link(click_count=5)
        link_store.get_by_short_code.return_value = link

        result = await manager.resolve_redirect("abc123")

        assert result.target_url == "https://example.com"
        assert result.click_count == 5
        assert result.created_by == "user-1"
        link_store.get_by_short_code.assert_awaited_once_with("abc123", active_only=True)
        link_store.increment_click_count.assert_awaited_once_with(link)
        link_store.commit.assert_awaited_once()
        link_store.refresh.assert_awaited_once_with(link)
        publisher.publish.assert_awaited_once()

    async def test_resolve_redirect_link_not_found(
        self, manager: RedirectManager, link_store: AsyncMock
    ) -> None:
        link_store.get_by_short_code.return_value = None

        with pytest.raises(LinkNotFoundError):
            await manager.resolve_redirect("missing")

    async def test_resolve_redirect_link_expired(
        self, manager: RedirectManager, link_store: AsyncMock
    ) -> None:
        expired_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        link = _make_link(expires_at=expired_at.replace(tzinfo=None))
        link_store.get_by_short_code.return_value = link

        with pytest.raises(LinkExpiredError):
            await manager.resolve_redirect("expired")

    async def test_publisher_failure_does_not_fail_redirect(
        self, manager: RedirectManager, link_store: AsyncMock, publisher: AsyncMock
    ) -> None:
        link = _make_link(click_count=1)
        link_store.get_by_short_code.return_value = link
        publisher.publish.side_effect = RuntimeError("queue down")

        result = await manager.resolve_redirect("abc123")

        assert result.target_url == "https://example.com"
        assert result.click_count == 1
