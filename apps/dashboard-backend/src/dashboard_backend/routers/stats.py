"""Dashboard stats router."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard_backend.clerk import ClerkUser, get_current_user
from snip_db import get_session
from snip_db.models import Link

router = APIRouter(prefix="/stats", tags=["stats"])


class StatsResponse(BaseModel):
    total_links: int
    total_clicks: int
    active_links: int
    expired_links: int


@router.get("", response_model=StatsResponse)
async def get_stats(
    user: ClerkUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    base = select(Link).where(Link.org_id == user.org_id)

    total = (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    clicks = (
        await session.execute(
            select(func.coalesce(func.sum(Link.click_count), 0)).where(Link.org_id == user.org_id)
        )
    ).scalar_one()
    active = (
        await session.execute(
            select(func.count()).where(Link.org_id == user.org_id, Link.is_active.is_(True))
        )
    ).scalar_one()
    expired = (
        await session.execute(
            select(func.count()).where(
                Link.org_id == user.org_id, Link.expires_at < datetime.utcnow()
            )
        )
    ).scalar_one()

    return {
        "total_links": total,
        "total_clicks": clicks,
        "active_links": active,
        "expired_links": expired,
    }
