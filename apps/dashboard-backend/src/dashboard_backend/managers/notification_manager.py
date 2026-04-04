"""Notification business logic manager."""

import html as html_mod
from typing import Dict, Optional

import httpx
from snip_email import EmailClient, EmailMessage
from snip_logger import get_logger

_log = get_logger("dashboard-backend", log_prefix="NotificationManager")

_CLICK_NOTIFICATION_FLAG = "click_notifications"


class NotificationManager:
    def __init__(
        self,
        email_client: EmailClient,
        feature_flags: Dict[str, bool],
        clerk_secret_key: str,
        click_threshold: int,
    ) -> None:
        self._email_client = email_client
        self._feature_flags = feature_flags
        self._clerk_secret_key = clerk_secret_key
        self._click_threshold = click_threshold

    async def maybe_notify_click_threshold(
        self,
        click_count: int,
        short_code: str,
        target_url: str,
        created_by: Optional[str],
    ) -> None:
        """Send notification if click_count just crossed the threshold."""
        if click_count != self._click_threshold:
            return

        if not self._feature_flags.get(_CLICK_NOTIFICATION_FLAG, False):
            return

        if not created_by:
            _log.warning("no_creator_for_link", short_code=short_code)
            return

        email = await self._get_user_email(created_by)
        if not email:
            _log.warning("email_not_resolved", user_id=created_by)
            return

        message = EmailMessage(
            to=[email],
            subject=f"Your link /{short_code} hit {self._click_threshold} clicks!",
            html=self._build_html(short_code, target_url, self._click_threshold),
        )

        try:
            await self._email_client.send(message)
            _log.info("click_threshold_email_sent", short_code=short_code, to=email)
        except Exception:
            _log.exception("click_threshold_email_failed", short_code=short_code)

    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Fetch user email from Clerk Backend API."""
        if not self._clerk_secret_key or self._clerk_secret_key == "sk_test_...":
            return "dev@example.com"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://api.clerk.com/v1/users/{user_id}",
                    headers={"Authorization": f"Bearer {self._clerk_secret_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
                for addr in data.get("email_addresses", []):
                    if addr.get("id") == data.get("primary_email_address_id"):
                        return addr.get("email_address")
                addrs = data.get("email_addresses", [])
                return addrs[0]["email_address"] if addrs else None
        except Exception:
            _log.exception("clerk_email_fetch_failed", user_id=user_id)
            return None

    @staticmethod
    def _build_html(short_code: str, target_url: str, threshold: int) -> str:
        safe_url = html_mod.escape(target_url)
        safe_code = html_mod.escape(short_code)
        return (
            '<div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">'
            "<h2>Milestone reached!</h2>"
            f"<p>Your link <strong>/{safe_code}</strong> just hit "
            f"<strong>{threshold}</strong> clicks.</p>"
            f'<p>Target: <a href="{safe_url}">{safe_url}</a></p>'
            '<p style="color: #888; font-size: 12px;">— Snip</p>'
            "</div>"
        )
