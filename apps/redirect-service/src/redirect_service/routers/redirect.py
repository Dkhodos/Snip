"""Public redirect endpoint."""

from html import escape

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from redirect_service.config import settings
from redirect_service.crawler_detection import is_crawler
from redirect_service.dependencies import get_redirect_manager
from redirect_service.managers.redirect_manager import RedirectManager, RedirectResult

router = APIRouter(tags=["redirect"])

_OG_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{click_count} clicks · {short_code}" />
  <meta property="og:image" content="{og_image_url}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:url" content="{redirect_url}" />
  <meta property="og:type" content="website" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{click_count} clicks · {short_code}" />
  <meta name="twitter:image" content="{og_image_url}" />
  <meta http-equiv="refresh" content="0;url={target_url}" />
</head>
<body>Redirecting…</body>
</html>"""


def _build_og_html(result: RedirectResult) -> str:
    title = escape(result.title or result.short_code)
    og_image_url = f"{settings.og_image_base_url.rstrip('/')}/{result.short_code}.png"
    redirect_url = f"{settings.redirect_base_url.rstrip('/')}/r/{result.short_code}"
    click_count_str = "1 click" if result.click_count == 1 else f"{result.click_count:,} clicks"
    return _OG_HTML_TEMPLATE.format(
        title=title,
        og_image_url=og_image_url,
        redirect_url=redirect_url,
        target_url=result.target_url,
        short_code=result.short_code,
        click_count=click_count_str,
    )


@router.get("/r/{short_code}", response_model=None)
async def redirect_to_target(
    short_code: str,
    request: Request,
    manager: RedirectManager = Depends(get_redirect_manager),
) -> RedirectResponse | HTMLResponse:
    user_agent = request.headers.get("user-agent")
    country = request.headers.get("cf-ipcountry")
    result = await manager.resolve_redirect(short_code, user_agent=user_agent, country=country)

    if is_crawler(user_agent):
        return HTMLResponse(content=_build_og_html(result), status_code=200)

    return RedirectResponse(url=result.target_url, status_code=302)
