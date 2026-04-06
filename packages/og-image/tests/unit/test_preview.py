"""Tests for snip_og_image.preview — HTML extraction and site preview fetching."""

import io
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image

from snip_og_image.models import SitePreview
from snip_og_image.preview import extract_favicon_url, extract_og_image_url, fetch_site_preview


class TestExtractOgImageUrl:
    def test_standard_attribute_order(self) -> None:
        html = '<meta property="og:image" content="https://example.com/img.png"/>'
        assert extract_og_image_url(html) == "https://example.com/img.png"

    def test_reversed_attribute_order(self) -> None:
        html = '<meta content="https://example.com/img.png" property="og:image"/>'
        assert extract_og_image_url(html) == "https://example.com/img.png"

    def test_returns_none_when_absent(self) -> None:
        assert extract_og_image_url("<html><head></head></html>") is None


class TestExtractFaviconUrl:
    def test_link_rel_icon(self) -> None:
        html = '<link rel="icon" href="/favicon.png"/>'
        assert extract_favicon_url(html, "https://example.com") == "https://example.com/favicon.png"

    def test_shortcut_icon(self) -> None:
        html = '<link rel="shortcut icon" href="/static/fav.ico"/>'
        assert (
            extract_favicon_url(html, "https://example.com") == "https://example.com/static/fav.ico"
        )

    def test_reversed_attribute_order(self) -> None:
        html = '<link href="/img/icon.png" rel="icon"/>'
        assert (
            extract_favicon_url(html, "https://example.com") == "https://example.com/img/icon.png"
        )

    def test_absolute_href_preserved(self) -> None:
        html = '<link rel="icon" href="https://cdn.example.com/favicon.ico"/>'
        assert (
            extract_favicon_url(html, "https://example.com")
            == "https://cdn.example.com/favicon.ico"
        )

    def test_falls_back_to_favicon_ico(self) -> None:
        assert (
            extract_favicon_url("<html></html>", "https://example.com/page")
            == "https://example.com/favicon.ico"
        )


class TestFetchSitePreview:
    async def test_returns_thumbnail_when_og_image_found(self) -> None:
        png_buf = io.BytesIO()
        Image.new("RGB", (400, 300), (0, 128, 255)).save(png_buf, format="PNG")
        png_bytes = png_buf.getvalue()

        html = '<meta property="og:image" content="https://example.com/img.png"/>'
        mock_page = MagicMock(text=html, url="https://example.com/")
        mock_img = MagicMock(content=png_bytes)
        mock_img.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[mock_page, mock_img])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("snip_og_image.preview.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_site_preview("https://example.com")

        assert result.thumbnail is not None
        assert result.domain == "example.com"

    async def test_returns_favicon_when_no_og_image(self) -> None:
        ico_buf = io.BytesIO()
        Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(ico_buf, format="PNG")
        ico_bytes = ico_buf.getvalue()

        html = '<link rel="icon" href="/favicon.ico"/>'
        mock_page = MagicMock(text=html, url="https://example.com/")
        mock_fav = MagicMock(content=ico_bytes)
        mock_fav.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[mock_page, mock_fav])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("snip_og_image.preview.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_site_preview("https://example.com")

        assert result.favicon is not None
        assert result.domain == "example.com"

    async def test_returns_empty_preview_on_fetch_failure(self) -> None:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("snip_og_image.preview.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_site_preview("https://example.com/page")

        assert result.thumbnail is None
        assert result.favicon is None
        assert result.domain == "example.com"

    async def test_returns_domain_only_preview_on_no_favicon(self) -> None:
        """Falls back gracefully when both og:image and favicon fetches fail."""
        html = "<html><head></head></html>"
        mock_page = MagicMock(text=html, url="https://example.com/")
        mock_fav = MagicMock()
        mock_fav.raise_for_status = MagicMock(side_effect=Exception("404"))

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[mock_page, mock_fav])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("snip_og_image.preview.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_site_preview("https://example.com")

        assert isinstance(result, SitePreview)
        assert result.domain == "example.com"
