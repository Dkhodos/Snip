"""Links CRUD router."""

from datetime import datetime
from uuid import UUID

import shortuuid
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard_backend.clerk import ClerkUser, get_current_user
from snip_db import get_session
from snip_db.models import Link

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
    session: AsyncSession = Depends(get_session),
) -> Link:
    short_code = body.custom_short_code or shortuuid.uuid()[:8]

    # Check for collision
    existing = await session.execute(select(Link).where(Link.short_code == short_code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Short code already in use")

    link = Link(
        org_id=user.org_id,
        short_code=short_code,
        target_url=body.target_url,
        title=body.title,
        created_by=user.user_id,
    )
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return link


ALLOWED_SORT_FIELDS = {"created_at", "click_count", "title"}


@router.get("", response_model=LinkListResponse)
async def list_links(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    status: str | None = Query(None),
    user: ClerkUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"sort_by must be one of: {', '.join(sorted(ALLOWED_SORT_FIELDS))}",
        )
    if sort_order not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="sort_order must be 'asc' or 'desc'")

    offset = (page - 1) * limit

    # Base filter
    base_filter = [Link.org_id == user.org_id]

    # Search filter
    if search:
        search_pattern = f"%{search}%"
        base_filter.append(
            (Link.title.ilike(search_pattern)) | (Link.short_code.ilike(search_pattern))
        )

    # Status filter
    if status == "active":
        base_filter.append(Link.is_active.is_(True))
    elif status == "inactive":
        base_filter.append(Link.is_active.is_(False))
    elif status == "expired":
        base_filter.append(Link.expires_at < datetime.utcnow())

    # Count total
    count_query = select(func.count()).select_from(Link).where(*base_filter)
    total = (await session.execute(count_query)).scalar_one()

    # Sort
    sort_column = getattr(Link, sort_by)
    order = sort_column.asc() if sort_order == "asc" else sort_column.desc()

    # Fetch page
    query = (
        select(Link)
        .where(*base_filter)
        .order_by(order)
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(query)
    links = result.scalars().all()

    return {"items": links, "total": total, "page": page, "limit": limit}


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Link:
    query = select(Link).where(Link.id == link_id, Link.org_id == user.org_id)
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.patch("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: UUID,
    body: UpdateLinkRequest,
    user: ClerkUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Link:
    query = select(Link).where(Link.id == link_id, Link.org_id == user.org_id)
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(link, field, value)

    await session.commit()
    await session.refresh(link)
    return link


@router.delete("/{link_id}", status_code=204)
async def delete_link(
    link_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    query = select(Link).where(Link.id == link_id, Link.org_id == user.org_id)
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    link.is_active = False
    await session.commit()
