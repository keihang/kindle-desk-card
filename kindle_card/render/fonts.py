from PIL import ImageFont
from pathlib import Path

FONT_SEARCH_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = ("bold" if bold else "regular", size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    for path in FONT_SEARCH_PATHS:
        if Path(path).exists():
            try:
                font = ImageFont.truetype(path, size)
                _FONT_CACHE[key] = font
                return font
            except Exception:
                continue

    font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font
