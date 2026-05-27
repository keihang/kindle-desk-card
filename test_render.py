"""Local preview: render widgets to PNG without pushing to Kindle."""

import sys
sys.path.insert(0, ".")

from kindle_card.config import load
from kindle_card.data import weather, datetime_info, todo, pokemon, quote, claude_status
from kindle_card.render.canvas import render


def main():
    config = load()
    city = config.get("weather", {}).get("city", "Zhongshan")

    data = {
        "top-left": {"type": "weather", "data": weather.fetch(city)},
        "top-right": {"type": "datetime", "data": datetime_info.fetch()},
        "middle-left": {"type": "todo", "data": todo.fetch(config.get("todo", {}))},
        "middle-right-top": {"type": "pokemon", "data": pokemon.fetch()},
        "middle-right-bottom": {"type": "quote", "data": quote.fetch()},
        "bottom": {"type": "claude_status", "data": claude_status.fetch()},
    }

    img = render(data)

    out_path = "/Users/keihang/Desktop/kindle_card_preview.png"
    img.save(out_path)
    print(f"Preview saved to {out_path}")
    print(f"Size: {img.size}")


if __name__ == "__main__":
    main()
