from PIL import ImageDraw
from .fonts import get_font

WHITE = 255
BLACK = 0
GRAY = 128
LIGHT_GRAY = 200


def _draw_separator(draw: ImageDraw.Draw, x: int, y: int, width: int):
    draw.line([(x, y), (x + width, y)], fill=GRAY, width=1)


_CITY_CN = {
    "Zhongshan": "中山", "Beijing": "北京", "Shanghai": "上海",
    "Guangzhou": "广州", "Shenzhen": "深圳", "Chengdu": "成都",
    "Hangzhou": "杭州", "Nanjing": "南京", "Wuhan": "武汉",
}


def paint_weather(draw: ImageDraw.Draw, rect: tuple, data: dict):
    x, y, w, h = rect
    font_body = get_font(36)
    font_small = get_font(28)

    city = _CITY_CN.get(data.get("city", ""), data.get("city", "--"))
    temp = data.get("temp", "--")
    condition = data.get("condition", "")
    forecast = data.get("forecast", [])

    # Left half: temperature + condition
    temp_str = f"{temp}°C"
    draw.text((x, y + 20), temp_str, fill=BLACK, font=get_font(56, bold=True))
    draw.text((x, y + 90), condition, fill=GRAY, font=font_body)

    # Right half: big city name
    font_city = get_font(85, bold=True)
    draw.text((x + w // 2, y - 10), city, fill=BLACK, font=font_city)

    _draw_separator(draw, x, y + 140, w)

    # 3-day forecast: condition on one line, temp below
    for i, day in enumerate(forecast[:3]):
        fy = y + 155 + i * 70
        date_str = day.get("date", "")
        cond = day.get("condition", "")
        if len(cond) > 16:
            cond = cond[:16] + "…"
        draw.text((x, fy), f"{date_str}  {cond}", fill=BLACK, font=font_small)
        draw.text((x, fy + 32), f"{day.get('low', '?')}° ~ {day.get('high', '?')}°", fill=GRAY, font=font_small)


def paint_datetime(draw: ImageDraw.Draw, rect: tuple, data: dict):
    x, y, w, h = rect
    time_str = data.get("time", "00:00")
    date_str = data.get("date", "")
    weekday = data.get("weekday", "")

    draw.text((x, y), time_str, fill=BLACK, font=get_font(96, bold=True))
    draw.text((x, y + 115), date_str, fill=GRAY, font=get_font(36))
    draw.text((x, y + 165), weekday, fill=GRAY, font=get_font(36))
    draw.text((x, y + 225), "阿恒", fill=BLACK, font=get_font(72, bold=True))
    draw.text((x, y + 310), "公众号：阿恒识滴AI", fill=BLACK, font=get_font(28, bold=True))
    draw.text((x, y + 345), "专注分享AI前沿资讯", fill=BLACK, font=get_font(28, bold=True))
    draw.text((x, y + 375), "AI知识干货分享", fill=BLACK, font=get_font(28, bold=True))


def paint_todo(draw: ImageDraw.Draw, rect: tuple, data: dict):
    x, y, w, h = rect
    font_title = get_font(60, bold=True)
    font_body = get_font(38)
    font_small = get_font(24)

    draw.text((x, y), "今日项目安排", fill=BLACK, font=font_title)
    _draw_separator(draw, x, y + 75, w)

    items = data.get("items", [])
    row_height = 55
    start_y = y + 95

    for i, item in enumerate(items[:10]):
        iy = start_y + i * row_height
        if iy + 35 > y + h:
            break
        # Checkbox
        draw.rectangle([(x, iy + 6), (x + 24, iy + 30)], outline=BLACK, width=2)
        # Task text
        title = item.get("title", "")
        if len(title) > 28:
            title = title[:26] + "..."
        draw.text((x + 36, iy), title, fill=BLACK, font=font_body)
        # Due label
        due = item.get("due", "")
        if due:
            draw.text((x + w - 150, iy + 3), due, fill=GRAY, font=font_small)
        # Row separator line
        _draw_separator(draw, x, iy + row_height - 5, w)

    # Bottom separator
    if items:
        last_y = start_y + min(len(items), 10) * row_height - 5
        return last_y
    else:
        draw.text((x, start_y), "暂无待办", fill=GRAY, font=font_body)
        return start_y + 50


def paint_pokemon(draw: ImageDraw.Draw, rect: tuple, data: dict):
    x, y, w, h = rect
    if not data or not data.get("name"):
        return

    font_title = get_font(28, bold=True)
    font_body = get_font(26)
    font_small = get_font(22)

    draw.text((x, y), "今日幸运pokemon", fill=GRAY, font=font_small)
    poke_name = f"#{data['id']} {data['name']}"
    draw.text((x, y + 30), poke_name, fill=BLACK, font=font_title)
    types = data.get("types", "")
    if types:
        draw.text((x, y + 65), types, fill=GRAY, font=font_body)
    stats_line = f"HP:{data.get('hp','-')}  ATK:{data.get('atk','-')}"
    draw.text((x, y + 95), stats_line, fill=GRAY, font=font_small)
    stats_line2 = f"DEF:{data.get('defense','-')}  SPE:{data.get('speed','-')}"
    draw.text((x, y + 120), stats_line2, fill=GRAY, font=font_small)


def paint_quote(draw: ImageDraw.Draw, rect: tuple, data: dict):
    x, y, w, h = rect
    if not data or not data.get("text"):
        return

    font_body = get_font(28)
    font_small = get_font(24)

    draw.text((x, y), "今日鸡汤", fill=BLACK, font=get_font(32, bold=True))
    text = data.get("text", "")
    font_quote = get_font(32)
    # Wrap based on pixel width
    max_width = w - 10
    bbox = draw.textbbox((0, 0), text, font=font_quote)
    if bbox[2] - bbox[0] > max_width:
        # Find wrap point by measuring character by character
        for i in range(len(text), 0, -1):
            if draw.textbbox((0, 0), text[:i], font=font_quote)[2] <= max_width:
                line1 = text[:i]
                line2 = text[i:]
                break
        else:
            line1, line2 = text, ""
        draw.text((x, y + 38), line1, fill=BLACK, font=font_quote)
        if line2:
            draw.text((x, y + 76), line2, fill=BLACK, font=font_quote)
    else:
        draw.text((x, y + 38), text, fill=BLACK, font=font_quote)
    author = data.get("author", "")
    if author:
        draw.text((x, y + 100), f"— {author}", fill=GRAY, font=font_small)


def _draw_claude_crab(draw: ImageDraw.Draw, cx: int, cy: int, size: int, fill: int = BLACK):
    """Draw Claude pixel crab logo."""
    p = size / 16  # pixel unit

    body_color = 120  # orange → gray
    dark_color = fill

    # Arms (row 6-7, extend left and right)
    draw.rectangle([(cx - 6*p, cy - 1*p), (cx - 3*p, cy + 1*p)], fill=body_color)
    draw.rectangle([(cx + 3*p, cy - 1*p), (cx + 6*p, cy + 1*p)], fill=body_color)

    # Body (rows 1-9)
    draw.rectangle([(cx - 4*p, cy - 5*p), (cx + 4*p, cy + 4*p)], fill=body_color)

    # Eyes (rows 2-3)
    draw.rectangle([(cx - 3*p, cy - 3*p), (cx - 2*p, cy - 1*p)], fill=dark_color)
    draw.rectangle([(cx + 2*p, cy - 3*p), (cx + 3*p, cy - 1*p)], fill=dark_color)

    # Legs (row 10-11)
    for lx in [-3, -1, 1, 3]:
        draw.rectangle([(cx + lx*p - 0.5*p, cy + 5*p), (cx + lx*p + 0.5*p, cy + 7*p)], fill=body_color)


def paint_claude_status(draw: ImageDraw.Draw, rect: tuple, data: dict):
    x, y, w, h = rect

    if data.get("error"):
        draw.text((x, y), "Claude Code", fill=BLACK, font=get_font(28, bold=True))
        draw.text((x, y + 35), "No stats available", fill=GRAY, font=get_font(22))
        return

    model = data.get("top_model", "--")
    total_tokens = data.get("total_tokens", "0")
    total_msgs = data.get("total_messages", 0)
    active = data.get("active_days", 0)
    days_since = data.get("days_since_first", 0)
    ctx_pct = int(active / days_since * 100) if days_since > 0 else 0

    font_label = get_font(22, bold=True)
    font_value = get_font(32, bold=True)

    logo_size = 70
    logo_x = x + w - logo_size // 2
    logo_cy = y + 40

    cy = y

    # MODEL (left)
    draw.text((x, cy), "MODEL", fill=GRAY, font=font_label)
    draw.text((x, cy + 28), model, fill=BLACK, font=font_value)

    # SESSION (center) — total messages
    sl_bbox = draw.textbbox((0, 0), "SESSION", font=font_label)
    sv_bbox = draw.textbbox((0, 0), f"{total_msgs:,}", font=font_value)
    sl_w = sl_bbox[2] - sl_bbox[0]
    sv_w = sv_bbox[2] - sv_bbox[0]
    center_x = x + (w - logo_size) // 2
    draw.text((center_x - sl_w // 2, cy), "SESSION", fill=GRAY, font=font_label)
    draw.text((center_x - sv_w // 2, cy + 28), f"{total_msgs:,}", fill=BLACK, font=font_value)

    # Claude crab logo (right)
    _draw_claude_crab(draw, logo_x, logo_cy, logo_size, fill=BLACK)

    cy += 72

    # CONTEXT WINDOW label (centered)
    ctx_bbox = draw.textbbox((0, 0), "CONTEXT WINDOW", font=font_label)
    ctx_w = ctx_bbox[2] - ctx_bbox[0]
    draw.text((x + (w - ctx_w) // 2, cy), "CONTEXT WINDOW", fill=GRAY, font=font_label)
    cy += 28

    # Progress bar
    bar_h = 32
    bar_bg = 200
    corner_r = bar_h // 2
    draw.rounded_rectangle(
        [(x, cy), (x + w, cy + bar_h)],
        radius=corner_r, fill=bar_bg, outline=BLACK, width=1
    )

    fill_w = max(bar_h, int(w * ctx_pct / 100))
    if fill_w > 2:
        draw.rounded_rectangle(
            [(x, cy), (x + fill_w, cy + bar_h)],
            radius=corner_r, fill=BLACK
        )

    font_bar = get_font(22, bold=True)
    bar_text = f"{ctx_pct}%  {total_tokens}"
    bbox = draw.textbbox((0, 0), bar_text, font=font_bar)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x + (w - tw) // 2
    ty = cy + (bar_h - th) // 2 - 2
    draw.text((tx, ty), bar_text, fill=WHITE, font=font_bar)
