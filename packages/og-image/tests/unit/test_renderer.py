"""Tests for snip_og_image.renderer — Pillow image generation."""

from PIL import Image

from snip_og_image.models import OgImageData, SitePreview
from snip_og_image.renderer import generate_image

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _make_data(**kwargs) -> OgImageData:
    defaults = dict(
        title="Test Link",
        short_code="abc123",
        click_count=5,
        redirect_base_url="http://localhost:8001",
    )
    defaults.update(kwargs)
    return OgImageData(**defaults)


class TestGenerateImage:
    def test_returns_valid_png(self) -> None:
        assert generate_image(_make_data())[:8] == _PNG_MAGIC

    def test_none_title_falls_back_to_short_code(self) -> None:
        assert len(generate_image(_make_data(title=None))) > 0

    def test_long_title_does_not_raise(self) -> None:
        assert len(generate_image(_make_data(title="A" * 200))) > 0

    def test_singular_click_count(self) -> None:
        assert len(generate_image(_make_data(click_count=1))) > 0

    def test_zero_click_count(self) -> None:
        assert len(generate_image(_make_data(click_count=0))) > 0

    def test_with_og_image_thumbnail(self) -> None:
        preview = SitePreview(
            thumbnail=Image.new("RGB", (400, 300), (200, 200, 200)),
            domain="example.com",
        )
        assert generate_image(_make_data(), preview)[:8] == _PNG_MAGIC

    def test_with_favicon_fallback(self) -> None:
        preview = SitePreview(
            favicon=Image.new("RGBA", (32, 32), (255, 100, 0, 255)),
            domain="example.com",
        )
        assert generate_image(_make_data(), preview)[:8] == _PNG_MAGIC

    def test_with_domain_only_preview(self) -> None:
        preview = SitePreview(domain="example.com")
        assert generate_image(_make_data(), preview)[:8] == _PNG_MAGIC

    def test_with_empty_preview(self) -> None:
        assert generate_image(_make_data(), SitePreview())[:8] == _PNG_MAGIC
