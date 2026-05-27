import time
import signal
import sys

from .config import load
from .data import weather, datetime_info, todo, pokemon, quote, claude_status
from .render.canvas import render
from .push import push_to_kindle


def collect_data(config: dict) -> dict:
    city = config.get("weather", {}).get("city", "Beijing")
    sources = [
        ("top-left", "weather", lambda: weather.fetch(city)),
        ("top-right", "datetime", lambda: datetime_info.fetch()),
        ("middle-left", "todo", lambda: todo.fetch(config.get("todo", {}))),
        ("middle-right-top", "pokemon", lambda: pokemon.fetch()),
        ("middle-right-bottom", "quote", lambda: quote.fetch()),
        ("bottom", "claude_status", lambda: claude_status.fetch()),
    ]
    data = {}
    for slot, wtype, fetcher in sources:
        try:
            data[slot] = {"type": wtype, "data": fetcher()}
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] {wtype} fetch failed: {e}")
            data[slot] = {"type": wtype, "data": {}}

    # 传递头像路径配置
    avatar_path = config.get("display", {}).get("avatar_path", "")
    if avatar_path:
        data["_avatar_path"] = avatar_path

    return data


def main():
    config = load()
    interval = config.get("refresh_interval", 600)

    running = True

    def on_signal(sig, frame):
        nonlocal running
        running = False
        print("\nShutting down...")

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    print(f"Kindle Desk Card daemon started (refresh every {interval}s)")

    while running:
        try:
            data = collect_data(config)
            img = render(data)
            push_to_kindle(img, config)
            print(f"[{time.strftime('%H:%M:%S')}] Frame pushed")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")

        for _ in range(interval):
            if not running:
                break
            time.sleep(1)

    print("Daemon stopped.")


if __name__ == "__main__":
    main()
