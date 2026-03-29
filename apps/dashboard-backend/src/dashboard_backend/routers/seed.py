"""Development seed data router."""

from fastapi import APIRouter, Depends, HTTPException

from dashboard_backend.config import settings
from dashboard_backend.dependencies import get_seed_manager
from dashboard_backend.managers.seed_manager import SeedManager

router = APIRouter(tags=["seed"])


@router.post("/seed")
async def seed_data(
    manager: SeedManager = Depends(get_seed_manager),
) -> dict:
    if settings.environment != "development":
        raise HTTPException(
            status_code=403, detail="Seed endpoint is only available in development"
        )

    return await manager.seed("dev_org")
