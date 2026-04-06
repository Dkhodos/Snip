"""Pillow-based OG image rendering."""

import functools
import io
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from snip_og_image.constants import (
    ACCENT_BAR_WIDTH,
    ACCENT_COLOR,
    BG_COLOR,
    BORDER_COLOR,
    BRAND_COLOR,
    BRAND_Y,
    CLICKS_BOTTOM_OFFSET,
    CONTENT_X,
    DIVIDER_VERTICAL_MARGIN,
    DOMAIN_LABEL_SPACING,
    FAVICON_SIZE,
    FAVICON_VERTICAL_OFFSET,
    HEIGHT,
    LABEL_FONT_SIZE,
    PANEL_COLOR,
    PANEL_PADDING_H,
    SEPARATOR_BOTTOM_OFFSET,
    SMALL_FONT_SIZE,
    SPLIT_X,
    THUMB_H,
    THUMB_RADIUS,
    THUMB_Y,
    TITLE_COLOR,
    TITLE_FONT_SIZE,
    TITLE_LINE_HEIGHT,
    TITLE_MAX_CHARS,
    TITLE_MAX_LINES,
    TITLE_START_Y,
    URL_BOTTOM_OFFSET,
    URL_COLOR,
    WIDTH,
)
from snip_og_image.models import OgImageData, SitePreview

_Font = ImageFont.FreeTypeFont | ImageFont.ImageFont


@functools.lru_cache(maxsize=1)
def _load_fonts() -> tuple[_Font, _Font, _Font]:
    try:
        title_font: _Font = ImageFont.load_default(size=TITLE_FONT_SIZE)
        label_font: _Font = ImageFont.load_default(size=LABEL_FONT_SIZE)
        small_font: _Font = ImageFont.load_default(size=SMALL_FONT_SIZE)
    except TypeError:
        # Older Pillow fallback — load_default() without size returns ImageFont
        _default = ImageFont.load_default()
        title_font = label_font = small_font = _default
    return title_font, label_font, small_font


def _wrap_text(text: str, max_chars: int, max_lines: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip() if current else word
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines[:max_lines]


def _rounded_rect_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return mask


def _draw_right_panel(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    preview: SitePreview,
) -> None:
    """Draw the right panel with either an og:image thumbnail or favicon + domain."""
    draw.rectangle([SPLIT_X + 1, 0, WIDTH, HEIGHT], fill=PANEL_COLOR)
    draw.line(
        [(SPLIT_X, DIVIDER_VERTICAL_MARGIN), (SPLIT_X, HEIGHT - DIVIDER_VERTICAL_MARGIN)],
        fill=BORDER_COLOR,
        width=1,
    )

    cx = (SPLIT_X + WIDTH) // 2
    _, _, small_font = _load_fonts()

    if preview.thumbnail is not None:
        tw, th = preview.thumbnail.size
        paste_x = cx - tw // 2
        paste_y = THUMB_Y + (THUMB_H - th) // 2
        mask = _rounded_rect_mask((tw, th), THUMB_RADIUS)
        img.paste(preview.thumbnail, (paste_x, paste_y), mask=mask)
        draw.rounded_rectangle(
            [paste_x, paste_y, paste_x + tw - 1, paste_y + th - 1],
            radius=THUMB_RADIUS,
            outline=BORDER_COLOR,
            width=1,
        )
        return

    # Favicon + domain fallback
    if preview.favicon is not None:
        fav = preview.favicon.resize((FAVICON_SIZE, FAVICON_SIZE), Image.Resampling.LANCZOS)
        paste_x = cx - FAVICON_SIZE // 2
        paste_y = HEIGHT // 2 - FAVICON_SIZE // 2 - FAVICON_VERTICAL_OFFSET
        if fav.mode == "RGBA":
            img.paste(fav, (paste_x, paste_y), mask=fav.split()[3])
        else:
            img.paste(fav.convert("RGB"), (paste_x, paste_y))
        domain_y = paste_y + FAVICON_SIZE + DOMAIN_LABEL_SPACING
    else:
        domain_y = HEIGHT // 2 - SMALL_FONT_SIZE // 2

    if preview.domain:
        draw.text((cx, domain_y), preview.domain, font=small_font, fill=URL_COLOR, anchor="mt")


def generate_image(
    data: OgImageData,
    preview: Optional[SitePreview] = None,
) -> bytes:
    """Render a 1200x630 PNG OG image using Pillow."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Left accent bar
    draw.rectangle([0, 0, ACCENT_BAR_WIDTH, HEIGHT], fill=ACCENT_COLOR)

    title_font, label_font, _ = _load_fonts()

    # Brand label
    draw.text((CONTENT_X, BRAND_Y), "snip ·", font=label_font, fill=BRAND_COLOR)

    # Title (wrapped, up to TITLE_MAX_LINES lines)
    title = (data.title or data.short_code).strip()
    lines = _wrap_text(title, max_chars=TITLE_MAX_CHARS, max_lines=TITLE_MAX_LINES)
    y = TITLE_START_Y
    for line in lines:
        draw.text((CONTENT_X, y), line, font=title_font, fill=TITLE_COLOR)
        y += TITLE_LINE_HEIGHT

    # Separator
    sep_y = HEIGHT - SEPARATOR_BOTTOM_OFFSET
    draw.line(
        [(CONTENT_X, sep_y), (SPLIT_X - PANEL_PADDING_H, sep_y)],
        fill=BORDER_COLOR,
        width=1,
    )

    _, _, small_font = _load_fonts()

    # Short URL
    short_url = f"{data.redirect_base_url}/r/{data.short_code}"
    draw.text((CONTENT_X, HEIGHT - URL_BOTTOM_OFFSET), short_url, font=small_font, fill=URL_COLOR)

    # Click count
    click_text = "1 click" if data.click_count == 1 else f"{data.click_count:,} clicks"
    draw.text(
        (CONTENT_X, HEIGHT - CLICKS_BOTTOM_OFFSET), click_text, font=small_font, fill=ACCENT_COLOR
    )

    # Right panel
    _draw_right_panel(img, draw, preview or SitePreview())

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
