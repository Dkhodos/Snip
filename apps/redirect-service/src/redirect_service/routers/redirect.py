"""Public redirect endpoint."""

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from redirect_service.dependencies import get_redirect_manager
from redirect_service.managers.redirect_manager import RedirectManager

router = APIRouter(tags=["redirect"])


@router.get("/r/{short_code}")
async def redirect_to_target(
    short_code: str,
    manager: RedirectManager = Depends(get_redirect_manager),
) -> RedirectResponse:
    result = await manager.resolve_redirect(short_code)
    return RedirectResponse(url=result.target_url, status_code=302)
