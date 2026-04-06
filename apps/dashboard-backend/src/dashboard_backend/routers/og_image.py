"""OG image generation router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from snip_auth import AuthUser
from snip_og_image import OgImageManager

from dashboard_backend.dependencies import get_current_user, get_link_manager, get_og_image_manager
from dashboard_backend.managers.link_manager import LinkManager

router = APIRouter(prefix="/links", tags=["og-image"])


class OgImageResponse(BaseModel):
    og_image_url: str


@router.post("/{link_id}/og-image", response_model=OgImageResponse)
async def generate_og_image(
    link_id: UUID,
    user: AuthUser = Depends(get_current_user),
    link_manager: LinkManager = Depends(get_link_manager),
    og_manager: OgImageManager | None = Depends(get_og_image_manager),
) -> OgImageResponse:
    """Regenerate and upload the OG image for a link. Returns the public URL."""
    if og_manager is None:
        raise HTTPException(status_code=501, detail="OG image generation not configured")
    link = await link_manager.get_link(link_id, user.org_id)
    og_image_url = await og_manager.generate_and_upload(link)
    return OgImageResponse(og_image_url=og_image_url)


@router.get("/{link_id}/og-image-url", response_model=OgImageResponse)
async def get_og_image_url(
    link_id: UUID,
    user: AuthUser = Depends(get_current_user),
    link_manager: LinkManager = Depends(get_link_manager),
    og_manager: OgImageManager | None = Depends(get_og_image_manager),
) -> OgImageResponse:
    """Return the deterministic OG image URL without regenerating."""
    if og_manager is None:
        raise HTTPException(status_code=501, detail="OG image generation not configured")
    link = await link_manager.get_link(link_id, user.org_id)
    return OgImageResponse(og_image_url=og_manager.get_og_image_url(link.short_code))
