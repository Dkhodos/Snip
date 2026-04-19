"""Data models for OG image generation."""

from dataclasses import dataclass, field

from PIL import Image


@dataclass(frozen=True)
class OgImageData:
    title: str | None
    short_code: str
    click_count: int
    redirect_base_url: str
    target_url: str | None = None


@dataclass
class SitePreview:
    """Result of fetching a site preview — either an og:image thumbnail or favicon + domain."""

    thumbnail: Image.Image | None = field(default=None)
    favicon: Image.Image | None = field(default=None)
    domain: str = ""
