"""Dashboard stats router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from snip_auth import AuthUser

from dashboard_backend.dependencies import get_current_user, get_link_manager
from dashboard_backend.managers.link_manager import LinkManager

router = APIRouter(prefix="/stats", tags=["stats"])


class StatsResponse(BaseModel):
    total_links: int
    total_clicks: int
    active_links: int
    expired_links: int


@router.get("", response_model=StatsResponse)
async def get_stats(
    user: AuthUser = Depends(get_current_user),
    manager: LinkManager = Depends(get_link_manager),
) -> dict:
    return await manager.get_stats(user.org_id)
