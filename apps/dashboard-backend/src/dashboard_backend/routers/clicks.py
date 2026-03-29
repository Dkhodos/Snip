"""Clicks analytics router."""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard_backend.clerk import ClerkUser, get_current_user
from snip_db import get_session
from snip_db.models import ClickEvent, Link

router = APIRouter(tags=["clicks"])


class DailyClicks(BaseModel):
    date: str
    count: int


class ClicksResponse(BaseModel):
    link_id: str
    total_clicks: int
    daily: list[DailyClicks]


class AggregateClicksResponse(BaseModel):
    daily: list[DailyClicks]


@router.get("/clicks/aggregate", response_model=AggregateClicksResponse)
async def get_aggregate_clicks(
    user: ClerkUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_query = (
        select(
            func.date(ClickEvent.clicked_at).label("date"),
            func.count().label("count"),
        )
        .join(Link, ClickEvent.link_id == Link.id)
        .where(Link.org_id == user.org_id, ClickEvent.clicked_at >= thirty_days_ago)
        .group_by(func.date(ClickEvent.clicked_at))
        .order_by(func.date(ClickEvent.clicked_at))
    )
    result = await session.execute(daily_query)
    daily = [{"date": str(row.date), "count": row.count} for row in result]

    return {"daily": daily}


@router.get("/links/{link_id}/clicks", response_model=ClicksResponse)
async def get_link_clicks(
    link_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    # Verify link belongs to org
    link_query = select(Link).where(Link.id == link_id, Link.org_id == user.org_id)
    result = await session.execute(link_query)
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Get daily clicks for last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_query = (
        select(
            func.date(ClickEvent.clicked_at).label("date"),
            func.count().label("count"),
        )
        .where(ClickEvent.link_id == link_id, ClickEvent.clicked_at >= seven_days_ago)
        .group_by(func.date(ClickEvent.clicked_at))
        .order_by(func.date(ClickEvent.clicked_at))
    )
    daily_result = await session.execute(daily_query)
    daily = [{"date": str(row.date), "count": row.count} for row in daily_result]

    return {
        "link_id": str(link_id),
        "total_clicks": link.click_count,
        "daily": daily,
    }
