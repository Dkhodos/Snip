"""Tests for NotificationManager."""

from unittest.mock import AsyncMock, MagicMock, patch

from dashboard_backend.managers.notification_manager import NotificationManager

_DEFAULT_FLAGS = {"click_notifications": True}


def _make_manager(
    *,
    flags: dict | None = None,
    clerk_key: str = "sk_test_...",
    threshold: int = 100,
) -> tuple[NotificationManager, AsyncMock]:
    email_client = AsyncMock()
    email_client.send.return_value = "msg_123"
    mgr = NotificationManager(
        email_client=email_client,
        feature_flags=_DEFAULT_FLAGS if flags is None else flags,
        clerk_secret_key=clerk_key,
        click_threshold=threshold,
    )
    return mgr, email_client


class TestMaybeNotifyClickThreshold:
    async def test_sends_at_threshold(self) -> None:
        mgr, email_client = _make_manager()
        await mgr.maybe_notify_click_threshold(
            click_count=100, short_code="abc", target_url="https://t.co", created_by="user_1"
        )
        email_client.send.assert_called_once()
        msg = email_client.send.call_args[0][0]
        assert msg.to == ["dev@example.com"]
        assert "abc" in msg.subject
        assert "100" in msg.subject

    async def test_skips_when_below_threshold(self) -> None:
        mgr, email_client = _make_manager()
        await mgr.maybe_notify_click_threshold(
            click_count=99, short_code="abc", target_url="https://t.co", created_by="user_1"
        )
        email_client.send.assert_not_called()

    async def test_skips_when_above_threshold(self) -> None:
        mgr, email_client = _make_manager()
        await mgr.maybe_notify_click_threshold(
            click_count=101, short_code="abc", target_url="https://t.co", created_by="user_1"
        )
        email_client.send.assert_not_called()

    async def test_skips_when_flag_disabled(self) -> None:
        mgr, email_client = _make_manager(flags={"click_notifications": False})
        await mgr.maybe_notify_click_threshold(
            click_count=100, short_code="abc", target_url="https://t.co", created_by="user_1"
        )
        email_client.send.assert_not_called()

    async def test_skips_when_flag_missing(self) -> None:
        mgr, email_client = _make_manager(flags={})
        await mgr.maybe_notify_click_threshold(
            click_count=100, short_code="abc", target_url="https://t.co", created_by="user_1"
        )
        email_client.send.assert_not_called()

    async def test_skips_when_no_creator(self) -> None:
        mgr, email_client = _make_manager()
        await mgr.maybe_notify_click_threshold(
            click_count=100, short_code="abc", target_url="https://t.co", created_by=None
        )
        email_client.send.assert_not_called()

    async def test_catches_send_error(self) -> None:
        mgr, email_client = _make_manager()
        email_client.send.side_effect = RuntimeError("API error")
        await mgr.maybe_notify_click_threshold(
            click_count=100, short_code="abc", target_url="https://t.co", created_by="user_1"
        )
        # Should not raise — error is logged

    async def test_skips_when_email_not_found(self) -> None:
        mgr, email_client = _make_manager(clerk_key="sk_live_real")
        with patch.object(mgr, "_get_user_email", return_value=None):
            await mgr.maybe_notify_click_threshold(
                click_count=100, short_code="abc", target_url="https://t.co", created_by="user_1"
            )
        email_client.send.assert_not_called()


class TestGetUserEmail:
    async def test_dev_mode_returns_dev_email(self) -> None:
        mgr, _ = _make_manager(clerk_key="sk_test_...")
        email = await mgr._get_user_email("user_1")
        assert email == "dev@example.com"

    async def test_empty_key_returns_dev_email(self) -> None:
        mgr, _ = _make_manager(clerk_key="")
        email = await mgr._get_user_email("user_1")
        assert email == "dev@example.com"

    async def test_real_key_calls_clerk_api(self) -> None:
        mgr, _ = _make_manager(clerk_key="sk_live_real")
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "primary_email_address_id": "email_1",
            "email_addresses": [
                {"id": "email_1", "email_address": "user@real.com"},
            ],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            email = await mgr._get_user_email("user_123")

        assert email == "user@real.com"
        mock_client.get.assert_called_once()
        call_url = mock_client.get.call_args[0][0]
        assert "user_123" in call_url

    async def test_clerk_api_error_returns_none(self) -> None:
        mgr, _ = _make_manager(clerk_key="sk_live_real")
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.side_effect = RuntimeError("Network error")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            email = await mgr._get_user_email("user_123")

        assert email is None
