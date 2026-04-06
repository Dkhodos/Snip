"""OgImageManager — orchestrates generation, upload, and URL resolution."""

import asyncio

from snip_db.models import Link
from snip_logger import get_logger
from snip_storage.protocol import StorageClient

from snip_og_image import renderer
from snip_og_image.models import OgImageData, SitePreview
from snip_og_image.preview import fetch_site_preview

_log = get_logger("snip-og-image", log_prefix="OgImageManager")


class OgImageManager:
    def __init__(
        self,
        storage_client: StorageClient,
        bucket: str,
        redirect_base_url: str,
        og_image_public_url_base: str,
    ) -> None:
        self._storage = storage_client
        self._bucket = bucket
        self._redirect_base_url = redirect_base_url
        self._og_image_public_url_base = og_image_public_url_base.rstrip("/")

    def get_og_image_url(self, short_code: str) -> str:
        return f"{self._og_image_public_url_base}/{short_code}.png"

    async def upload_image(self, short_code: str, image_data: bytes) -> str:
        key = f"{short_code}.png"
        await self._storage.upsert(self._bucket, key, image_data, content_type="image/png")
        return self.get_og_image_url(short_code)

    async def generate_and_upload(self, link: Link) -> str:
        preview: SitePreview | None = (
            await fetch_site_preview(link.target_url) if link.target_url else None
        )
        data = OgImageData(
            title=link.title,
            short_code=link.short_code,
            click_count=link.click_count,
            redirect_base_url=self._redirect_base_url,
            target_url=link.target_url,
        )
        image_bytes = await asyncio.to_thread(renderer.generate_image, data, preview)
        url = await self.upload_image(link.short_code, image_bytes)
        _log.info("og_image_generated", short_code=link.short_code, url=url)
        return url
