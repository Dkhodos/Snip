"""Feature flags router."""

import time

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from snip_db import get_session
from snip_db.models import FeatureFlag

router = APIRouter(prefix="/flags", tags=["flags"])

# Simple in-memory cache
_flags_cache: dict[str, bool] | None = None
_flags_cache_time: float = 0.0
_CACHE_TTL = 60.0  # seconds


@router.get("")
async def get_flags(
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    global _flags_cache, _flags_cache_time

    now = time.time()
    if _flags_cache is not None and (now - _flags_cache_time) < _CACHE_TTL:
        return _flags_cache

    result = await session.execute(select(FeatureFlag))
    flags = result.scalars().all()

    _flags_cache = {flag.key: flag.enabled for flag in flags}
    _flags_cache_time = now

    return _flags_cache
