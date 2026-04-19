"""Feature flags router."""

from fastapi import APIRouter, Depends

from dashboard_backend.dependencies import get_feature_flag_manager
from dashboard_backend.managers.feature_flag_manager import FeatureFlagManager

router = APIRouter(prefix="/flags", tags=["flags"])


@router.get("")
async def get_flags(
    manager: FeatureFlagManager = Depends(get_feature_flag_manager),
) -> dict[str, bool]:
    return await manager.get_all_flags()
