import os
import urllib.request
from io import BytesIO
from PIL import Image, ImageDraw
from . import widgets

# KPW3 framebuffer: 1088x1448, 8-bit grayscale
WIDTH = 1088
HEIGHT = 1448
VISIBLE_WIDTH = 1072
PADDING_X = (WIDTH - VISIBLE_WIDTH) // 2  # 8px each side

# Widget layout slots (x, y, w, h) — in visible area coordinates
SLOTS = {
    "top-left":     (40, 80, 480, 400),
    "top-right":    (580, 80, 450, 420),
    "middle-left":  (40, 540, 520, 860),
    "middle-right-top": (590, 540, 440, 200),
    "middle-right-bottom": (590, 760, 440, 200),
    "bottom": (40, 1130, 1000, 168),
}

WIDGET_PAINTERS = {
    "weather": widgets.paint_weather,
    "datetime": widgets.paint_datetime,
    "todo": widgets.paint_todo,
    "pokemon": widgets.paint_pokemon,
    "quote": widgets.paint_quote,
    "claude_status": widgets.paint_claude_status,
}

GRAY = 128


def _download_sprite(url: str, size: tuple = (200, 200)) -> Image.Image | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KindleCard/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            img = Image.open(BytesIO(resp.read())).convert("RGBA")
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            bg = bg.convert("L")
            bg.thumbnail(size, Image.LANCZOS)
            return bg
    except Exception:
        return None


def render(widget_data: dict[str, dict]) -> Image.Image:
    """Render all widgets onto a grayscale canvas."""
    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # Track todo bottom line position
    todo_bottom_y = 0

    # Draw widgets
    for slot_name, widget_info in widget_data.items():
        if slot_name not in SLOTS:
            continue
        wtype = widget_info.get("type")
        data = widget_info.get("data", {})
        painter = WIDGET_PAINTERS.get(wtype)
        if not painter:
            continue

        sx, sy, sw, sh = SLOTS[slot_name]
        rect = (sx + PADDING_X, sy, sw, sh)

        # Todo returns the bottom y position
        if wtype == "todo":
            todo_bottom_y = painter(draw, rect, data)
        else:
            painter(draw, rect, data)

        # Paste Pokémon sprite if available
        if wtype == "pokemon" and data.get("sprite"):
            sprite = _download_sprite(data["sprite"], (150, 150))
            if sprite:
                px = sx + PADDING_X + 280
                py = sy + 10
                img.paste(sprite, (px, py))

    # Separator line below weather/datetime area
    _tl_x, _tl_y, _tl_w, _tl_h = SLOTS["top-left"]
    line_y = _tl_y + _tl_h + 10
    draw.line([(PADDING_X + 40, line_y), (PADDING_X + 1040, line_y)], fill=GRAY, width=2)

    # Draw todo box: vertical line on right side of todo
    _ml_x, _ml_y, _ml_w, _ml_h = SLOTS["middle-left"]
    if todo_bottom_y > 0:
        todo_x = PADDING_X + _ml_x
        todo_right_x = PADDING_X + _ml_x + _ml_w
        todo_top_y = _ml_y + 75  # Below title + separator

        # Vertical line from top separator down to last item bottom
        draw.line([(todo_right_x, line_y), (todo_right_x, todo_bottom_y)], fill=GRAY, width=2)

        # Bottom line extends full width to the right (past quote area)
        full_right_x = PADDING_X + 1040
        draw.line([(todo_x, todo_bottom_y), (full_right_x, todo_bottom_y)], fill=GRAY, width=2)

    # Avatar image in right column, between quote and todo bottom line
    _qr_x, _qr_y, _qr_w, _qr_h = SLOTS["middle-right-bottom"]
    avatar_path = os.path.expanduser(widget_data.get("_avatar_path", ""))
    if avatar_path and os.path.exists(avatar_path):
        avatar = Image.open(avatar_path).convert("L")
        avatar.thumbnail((200, 200), Image.LANCZOS)
        ax = PADDING_X + _qr_x + (_qr_w - avatar.width) // 2
        ay = _qr_y + _qr_h // 2  # Center in quote slot
        img.paste(avatar, (ax, ay))

    return img
