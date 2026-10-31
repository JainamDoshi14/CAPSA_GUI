"""Neubrutalist light palette and component tokens."""

BG = "#FFF6E0"
SURFACE = "#FFFFFF"
INK = "#111111"
MUTED = "#4A4A4A"
YELLOW = "#FFD93D"
PINK = "#FF6B9D"
BLUE = "#4D96FF"
MINT = "#6BCB77"
ORANGE = "#FF9F1C"
LAVENDER = "#C9B6FF"
RED = "#FF4D4D"
HOVER_TINT = "#FFF0B8"
ALT_SURFACE = "#FFFBEF"
GRID = "#E6DDC8"

BORDER_WIDTH = 3
SHADOW_NORMAL = 4
SHADOW_LARGE = 6
RADIUS = 4
FONT_DISPLAY = "Arial Black"   # Space Grotesk Bold fallback
FONT_BODY = "Segoe UI"         # Space Grotesk Medium fallback
FONT_BUTTON = "Arial"          # Space Grotesk Bold fallback
FONT_MONO = "Consolas"         # Space Mono fallback

# Compatibility names used by existing view logic.
COLORS = {
    "bg": BG,
    "surface": SURFACE,
    "surface_2": SURFACE,
    "border": INK,
    "hover": HOVER_TINT,
    "text": INK,
    "muted": MUTED,
    "primary": YELLOW,
    "primary_2": YELLOW,
    "pink": PINK,
    "amber": YELLOW,
    "sky": BLUE,
    "success": MINT,
    "warning": ORANGE,
    "orange": ORANGE,
    "mint": MINT,
    "lavender": LAVENDER,
    "yellow": YELLOW,
    "grid": GRID,
    "alt_surface": ALT_SURFACE,
    "error": RED,
}

PRIMARY_TEXT = INK
TYPE_L = BLUE
TYPE_C = PINK
TYPE_GMD = MINT
TYPE_GMR = ORANGE
