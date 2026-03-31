"""Public redirect endpoint."""

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse

from dashboard_backend.dependencies import get_notification_manager, get_redirect_manager
from dashboard_backend.managers.notification_manager import NotificationManager
from dashboard_backend.managers.redirect_manager import RedirectManager

router = APIRouter(tags=["redirect"])


@router.get("/r/{short_code}")
async def redirect_to_target(
    short_code: str,
    background_tasks: BackgroundTasks,
    manager: RedirectManager = Depends(get_redirect_manager),
    notification_manager: NotificationManager = Depends(get_notification_manager),
) -> RedirectResponse:
    result = await manager.resolve_redirect(short_code)
    background_tasks.add_task(
        notification_manager.maybe_notify_click_threshold,
        click_count=result.click_count,
        short_code=short_code,
        target_url=result.target_url,
        created_by=result.created_by,
    )
    return RedirectResponse(url=result.target_url, status_code=302)
