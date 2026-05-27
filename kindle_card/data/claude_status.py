"""Read real Claude Code usage stats from ~/.claude/stats-cache.json."""

import json
import os
from datetime import date, datetime


STATS_PATH = os.path.expanduser("~/.claude/stats-cache.json")


def _load_stats() -> dict:
    try:
        with open(STATS_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _top_model(model_usage: dict) -> tuple[str, int]:
    best_name, best_total = "--", 0
    for name, info in model_usage.items():
        total = info.get("inputTokens", 0) + info.get("outputTokens", 0)
        if total > best_total:
            best_name, best_total = name, total
    return best_name, best_total


def fetch(config=None) -> dict:
    stats = _load_stats()
    if not stats:
        return {"error": "no data"}

    today_str = date.today().isoformat()

    # Today's activity
    today_activity = {}
    for day in stats.get("dailyActivity", []):
        if day["date"] == today_str:
            today_activity = day
            break

    # Today's tokens (all models combined)
    today_tokens = 0
    for day in stats.get("dailyModelTokens", []):
        if day["date"] == today_str:
            today_tokens = sum(day.get("tokensByModel", {}).values())
            break

    # Top model
    model_usage = stats.get("modelUsage", {})
    top_model, top_tokens = _top_model(model_usage)

    # Total tokens across all models
    total_tokens = sum(
        m.get("inputTokens", 0) + m.get("outputTokens", 0)
        for m in model_usage.values()
    )

    # Active days count
    active_days = len(stats.get("dailyActivity", []))

    # Days since first session
    first_date = stats.get("firstSessionDate", "")
    if first_date:
        first = datetime.fromisoformat(first_date.replace("Z", "+00:00"))
        days_since = (datetime.now(first.tzinfo) - first).days
    else:
        days_since = 0

    return {
        "today_messages": today_activity.get("messageCount", 0),
        "today_sessions": today_activity.get("sessionCount", 0),
        "today_tools": today_activity.get("toolCallCount", 0),
        "today_tokens": _format_tokens(today_tokens),
        "total_messages": stats.get("totalMessages", 0),
        "total_sessions": stats.get("totalSessions", 0),
        "total_tokens": _format_tokens(total_tokens),
        "top_model": top_model.split("/")[-1] if "/" in top_model else top_model,
        "active_days": active_days,
        "days_since_first": days_since,
    }
