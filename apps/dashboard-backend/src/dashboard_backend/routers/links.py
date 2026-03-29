"""Links CRUD router."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from dashboard_backend.clients.clerk_client import ClerkUser
from dashboard_backend.dependencies import get_current_user, get_link_manager
from dashboard_backend.managers.link_manager import LinkManager

router = APIRouter(prefix="/links", tags=["links"])


class CreateLinkRequest(BaseModel):
    target_url: str
    title: str
    custom_short_code: str | None = None


class UpdateLinkRequest(BaseModel):
    target_url: str | None = None
    title: str | None = None
    is_active: bool | None = None


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


@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(
    body: CreateLinkRequest,
    user: ClerkUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> object:
    return await manager.create_link(
        org_id=user.org_id,
        user_id=user.user_id,
        target_url=body.target_url,
        title=body.title,
        custom_short_code=body.custom_short_code,
    )


@router.get("", response_model=LinkListResponse)
async def list_links(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    status: str | None = Query(None),
    user: ClerkUser = Depends(get_current_user),
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
    user: ClerkUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> object:
    return await manager.get_link(link_id, user.org_id)


@router.patch("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: UUID,
    body: UpdateLinkRequest,
    user: ClerkUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> object:
    update_data = body.model_dump(exclude_unset=True)
    return await manager.update_link(link_id, user.org_id, **update_data)


@router.delete("/{link_id}", status_code=204)
async def delete_link(
    link_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> None:
    await manager.delete_link(link_id, user.org_id)
