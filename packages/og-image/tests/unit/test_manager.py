"""Tests for snip_og_image.manager — OgImageManager orchestration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from snip_og_image import OgImageManager, SitePreview


def _make_link(
    *,
    short_code: str = "abc123",
    title: str | None = "My Test Link",
    click_count: int = 42,
    target_url: str | None = "https://example.com",
) -> MagicMock:
    link = MagicMock()
    link.short_code = short_code
    link.title = title
    link.click_count = click_count
    link.target_url = target_url
    return link


@pytest.fixture()
def storage_client() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def manager(storage_client: AsyncMock) -> OgImageManager:
    return OgImageManager(
        storage_client=storage_client,
        bucket="snip-og-images",
        redirect_base_url="http://localhost:8001",
        og_image_public_url_base="http://localhost:9000/snip-og-images",
    )


class TestGetOgImageUrl:
    def test_returns_deterministic_url(self, manager: OgImageManager) -> None:
        assert (
            manager.get_og_image_url("abc123") == "http://localhost:9000/snip-og-images/abc123.png"
        )

    def test_trailing_slash_stripped(self) -> None:
        m = OgImageManager(
            storage_client=AsyncMock(),
            bucket="bucket",
            redirect_base_url="http://localhost",
            og_image_public_url_base="http://localhost:9000/bucket/",
        )
        assert m.get_og_image_url("xyz") == "http://localhost:9000/bucket/xyz.png"


class TestUploadImage:
    async def test_calls_storage_upsert(
        self, manager: OgImageManager, storage_client: AsyncMock
    ) -> None:
        await manager.upload_image("abc123", b"fake-png-data")
        storage_client.upsert.assert_awaited_once_with(
            "snip-og-images", "abc123.png", b"fake-png-data", content_type="image/png"
        )

    async def test_returns_public_url(
        self, manager: OgImageManager, storage_client: AsyncMock
    ) -> None:
        assert (
            await manager.upload_image("abc123", b"data")
            == "http://localhost:9000/snip-og-images/abc123.png"
        )


class TestGenerateAndUpload:
    _PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

    async def test_uploads_valid_png(
        self, manager: OgImageManager, storage_client: AsyncMock
    ) -> None:
        link = _make_link(short_code="abc123", title="My Link", click_count=7)
        with patch(
            "snip_og_image.manager.fetch_site_preview",
            new=AsyncMock(return_value=SitePreview()),
        ):
            url = await manager.generate_and_upload(link)
        assert url == "http://localhost:9000/snip-og-images/abc123.png"
        assert storage_client.upsert.call_args[0][2][:8] == self._PNG_MAGIC

    async def test_uses_og_image_when_available(
        self, manager: OgImageManager, storage_client: AsyncMock
    ) -> None:
        link = _make_link()
        preview = SitePreview(
            thumbnail=Image.new("RGB", (300, 200), (0, 100, 200)),
            domain="example.com",
        )
        with patch("snip_og_image.manager.fetch_site_preview", new=AsyncMock(return_value=preview)):
            await manager.generate_and_upload(link)
        assert storage_client.upsert.call_args[0][2][:8] == self._PNG_MAGIC

    async def test_falls_back_to_favicon(
        self, manager: OgImageManager, storage_client: AsyncMock
    ) -> None:
        link = _make_link()
        preview = SitePreview(
            favicon=Image.new("RGBA", (32, 32), (255, 0, 0, 255)),
            domain="example.com",
        )
        with patch("snip_og_image.manager.fetch_site_preview", new=AsyncMock(return_value=preview)):
            await manager.generate_and_upload(link)
        assert storage_client.upsert.call_args[0][2][:8] == self._PNG_MAGIC

    async def test_no_target_url_skips_preview_fetch(
        self, manager: OgImageManager, storage_client: AsyncMock
    ) -> None:
        link = _make_link(target_url=None)
        with patch("snip_og_image.manager.fetch_site_preview", new=AsyncMock()) as mock_fetch:
            await manager.generate_and_upload(link)
        mock_fetch.assert_not_awaited()
