"""Data models for OG image generation."""

from dataclasses import dataclass, field
from typing import Optional

from PIL import Image


@dataclass(frozen=True)
class OgImageData:
    title: Optional[str]
    short_code: str
    click_count: int
    redirect_base_url: str
    target_url: Optional[str] = None


@dataclass
class SitePreview:
    """Result of fetching a site preview — either an og:image thumbnail or favicon + domain."""

    thumbnail: Optional[Image.Image] = field(default=None)
    favicon: Optional[Image.Image] = field(default=None)
    domain: str = ""
