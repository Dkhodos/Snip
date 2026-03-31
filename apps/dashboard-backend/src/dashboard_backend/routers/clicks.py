"""Clicks analytics router."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from snip_auth import AuthUser

from dashboard_backend.dependencies import get_clicks_manager, get_current_user
from dashboard_backend.managers.clicks_manager import ClicksManager

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
    user: AuthUser = Depends(get_current_user),
    manager: ClicksManager = Depends(get_clicks_manager),
) -> dict:
    return await manager.get_aggregate_clicks(user.org_id)


@router.get("/links/{link_id}/clicks", response_model=ClicksResponse)
async def get_link_clicks(
    link_id: UUID,
    user: AuthUser = Depends(get_current_user),
    manager: ClicksManager = Depends(get_clicks_manager),
) -> dict:
    return await manager.get_link_clicks(link_id, user.org_id)
