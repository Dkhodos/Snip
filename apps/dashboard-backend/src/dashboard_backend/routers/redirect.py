"""Public redirect endpoint."""

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from dashboard_backend.dependencies import get_redirect_manager
from dashboard_backend.managers.redirect_manager import RedirectManager

router = APIRouter(tags=["redirect"])


@router.get("/r/{short_code}")
async def redirect_to_target(
    short_code: str,
    manager: RedirectManager = Depends(get_redirect_manager),
) -> RedirectResponse:
    target_url = await manager.resolve_redirect(short_code)
    return RedirectResponse(url=target_url, status_code=302)
