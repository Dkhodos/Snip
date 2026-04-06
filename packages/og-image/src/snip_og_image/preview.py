"""Site preview fetching — og:image thumbnail or favicon + domain fallback."""

import io
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from PIL import Image
from snip_logger import get_logger

from snip_og_image.constants import FETCH_TIMEOUT, THUMB_H, THUMB_W
from snip_og_image.models import SitePreview

_log = get_logger("snip-og-image", log_prefix="preview")


def extract_og_image_url(html: str) -> Optional[str]:
    pattern = re.compile(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    m = pattern.search(html)
    if m:
        return m.group(1)
    pattern2 = re.compile(
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        re.IGNORECASE,
    )
    m2 = pattern2.search(html)
    return m2.group(1) if m2 else None


def extract_favicon_url(html: str, base_url: str) -> str:
    """Extract favicon URL from <link> tags, falling back to /favicon.ico."""
    pattern = re.compile(
        r'<link[^>]+rel=["\'][^"\']*(?:shortcut\s+)?icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    m = pattern.search(html)
    if not m:
        pattern2 = re.compile(
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*(?:shortcut\s+)?icon[^"\']*["\']',
            re.IGNORECASE,
        )
        m = pattern2.search(html)
    if m:
        return urljoin(base_url, m.group(1))
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"


async def fetch_site_preview(target_url: str) -> SitePreview:
    """
    Fetch the target page once and return a SitePreview:
    - If og:image found → thumbnail (scaled to panel size)
    - Otherwise → favicon + domain name
    Returns an empty SitePreview on any failure.
    """
    domain = urlparse(target_url).netloc
    try:
        headers = {"User-Agent": "SnipBot/1.0 (link preview)"}
        async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, follow_redirects=True) as client:
            page_resp = await client.get(target_url, headers=headers)
            html = page_resp.text
            base_url = str(page_resp.url)

            og_url = extract_og_image_url(html)
            if og_url:
                img_resp = await client.get(og_url, headers=headers)
                img_resp.raise_for_status()
                thumbnail = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
                thumbnail.thumbnail((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
                return SitePreview(thumbnail=thumbnail, domain=domain)

            # No og:image — fall back to favicon
            favicon_url = extract_favicon_url(html, base_url)
            fav_resp = await client.get(favicon_url, headers=headers)
            fav_resp.raise_for_status()
            favicon = Image.open(io.BytesIO(fav_resp.content)).convert("RGBA")
            return SitePreview(favicon=favicon, domain=domain)

    except Exception as exc:  # noqa: BLE001
        _log.warning("site_preview_fetch_failed", url=target_url, error=str(exc))
        return SitePreview(domain=domain)
