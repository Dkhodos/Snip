"""Links CRUD router."""

from datetime import datetime
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field, field_validator
from snip_auth import AuthUser
from snip_db.models import Link
from snip_logger import get_logger
from snip_og_image import OgImageManager

from dashboard_backend.dependencies import get_current_user, get_link_manager, get_og_image_manager
from dashboard_backend.managers.link_manager import LinkManager

_log = get_logger("dashboard-backend", log_prefix="LinksRouter")

router = APIRouter(prefix="/links", tags=["links"])

_ALLOWED_URL_SCHEMES = {"http", "https"}


def _validate_target_url(v: str) -> str:
    parsed = urlparse(v)
    if parsed.scheme.lower() not in _ALLOWED_URL_SCHEMES:
        raise ValueError("Only http and https URLs are allowed")
    return v


class CreateLinkRequest(BaseModel):
    target_url: str
    title: str
    custom_short_code: str | None = Field(
        None,
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )

    @field_validator("target_url")
    @classmethod
    def validate_target_url(cls, v: str) -> str:
        return _validate_target_url(v)


class UpdateLinkRequest(BaseModel):
    target_url: str | None = None
    title: str | None = None
    is_active: bool | None = None

    @field_validator("target_url")
    @classmethod
    def validate_target_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_target_url(v)


class LinkResponse(BaseModel):
    id: UUID
    org_id: str
    short_code: str
    target_url: str
    title: str | None
    click_count: int
    is_active: bool
    created_by: str | None
    created_at: datetime
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class LinkListResponse(BaseModel):
    items: list[LinkResponse]
    total: int
    page: int
    limit: int


async def _fire_og_generation(og_manager: OgImageManager, link: Link) -> None:
    try:
        await og_manager.generate_and_upload(link)
    except Exception:
        _log.warning("og_image_generation_failed", exc_info=True)


@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(
    body: CreateLinkRequest,
    background_tasks: BackgroundTasks,
    user: AuthUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
    og_manager: OgImageManager = Depends(get_og_image_manager),
) -> object:
    link = await manager.create_link(
        org_id=user.org_id,
        user_id=user.user_id,
        target_url=body.target_url,
        title=body.title,
        custom_short_code=body.custom_short_code,
    )
    background_tasks.add_task(_fire_og_generation, og_manager, link)
    return link


@router.get("", response_model=LinkListResponse)
async def list_links(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    status: Optional[str] = Query(None),
    user: AuthUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> dict:
    items, total = await manager.list_links(
        user.org_id,
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        status=status,
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: UUID,
    user: AuthUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> object:
    return await manager.get_link(link_id, user.org_id)


@router.patch("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: UUID,
    body: UpdateLinkRequest,
    background_tasks: BackgroundTasks,
    user: AuthUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
    og_manager: OgImageManager = Depends(get_og_image_manager),
) -> object:
    update_data = body.model_dump(exclude_unset=True)
    updated = await manager.update_link(link_id, user.org_id, **update_data)
    if any(f in update_data for f in ("title", "target_url")):
        background_tasks.add_task(_fire_og_generation, og_manager, updated)
    return updated


@router.delete("/{link_id}", status_code=204)
async def delete_link(
    link_id: UUID,
    user: AuthUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> None:
    await manager.delete_link(link_id, user.org_id)
