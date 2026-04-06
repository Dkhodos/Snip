"""Layout, palette, font, and network constants for OG image generation."""

# Image dimensions (standard 1.91:1 OG ratio)
WIDTH = 1200
HEIGHT = 630

# Left/right panel split (left panel 0–SPLIT_X, right panel SPLIT_X–WIDTH)
SPLIT_X = 660

# Left panel layout
CONTENT_X = 60
ACCENT_BAR_WIDTH = 8
BRAND_Y = 48
TITLE_START_Y = 140
TITLE_LINE_HEIGHT = 70
TITLE_MAX_CHARS = 32
TITLE_MAX_LINES = 3
SEPARATOR_BOTTOM_OFFSET = 170
URL_BOTTOM_OFFSET = 148
CLICKS_BOTTOM_OFFSET = 108
PANEL_PADDING_H = 40

# Right panel — thumbnail slot geometry
THUMB_Y = 60
THUMB_W = WIDTH - SPLIT_X - 80  # width of thumbnail slot in right panel
THUMB_H = HEIGHT - 120  # height of thumbnail slot in right panel
THUMB_RADIUS = 12

# Right panel — favicon fallback layout
FAVICON_SIZE = 96
FAVICON_VERTICAL_OFFSET = 30
DOMAIN_LABEL_SPACING = 20
DIVIDER_VERTICAL_MARGIN = 40

# Font sizes
TITLE_FONT_SIZE = 52
LABEL_FONT_SIZE = 30
SMALL_FONT_SIZE = 24

# Colors (RGB tuples)
BG_COLOR = (15, 23, 42)  # slate-900
ACCENT_COLOR = (99, 102, 241)  # indigo-500
TITLE_COLOR = (248, 250, 252)  # slate-50
URL_COLOR = (148, 163, 184)  # slate-400
BORDER_COLOR = (51, 65, 85)  # slate-700
BRAND_COLOR = (99, 102, 241)  # indigo-500
PANEL_COLOR = (22, 32, 56)  # slate-800

# Network
FETCH_TIMEOUT = 5.0
