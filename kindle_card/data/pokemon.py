"""Daily random Pokémon from PokeAPI."""

import json
import urllib.request
from datetime import date

TYPE_CN = {
    "Normal": "一般", "Fire": "火", "Water": "水", "Electric": "电",
    "Grass": "草", "Ice": "冰", "Fighting": "格斗", "Poison": "毒",
    "Ground": "地面", "Flying": "飞行", "Psychic": "超能力", "Bug": "虫",
    "Rock": "岩石", "Ghost": "幽灵", "Dragon": "龙", "Dark": "恶",
    "Steel": "钢", "Fairy": "妖精",
}


def _get_today_id() -> int:
    today = date.today()
    seed = today.year * 366 + today.timetuple().tm_yday
    return (seed * 997) % 1025 + 1


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "KindleCard/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch() -> dict:
    try:
        poke_id = _get_today_id()
        pokemon = _fetch_json(f"https://pokeapi.co/api/v2/pokemon/{poke_id}")

        name_en = pokemon["name"].replace("-", " ").title()
        types = [TYPE_CN.get(t["type"]["name"].title(), t["type"]["name"].title())
                 for t in pokemon["types"]]
        height = pokemon["height"] / 10
        weight = pokemon["weight"] / 10

        stats = {}
        for s in pokemon["stats"]:
            stats[s["stat"]["name"]] = s["base_stat"]

        # Get Chinese name
        name_cn = name_en
        try:
            species = _fetch_json(f"https://pokeapi.co/api/v2/pokemon-species/{poke_id}")
            names = {n["language"]["name"]: n["name"] for n in species.get("names", [])}
            for lang in ("zh-Hans", "zh-Hant", "ja-Hrkt", "ja"):
                if lang in names:
                    name_cn = names[lang]
                    break
        except Exception:
            pass

        sprite = (pokemon["sprites"]["other"]["official-artwork"]["front_default"]
                  or pokemon["sprites"]["front_default"] or "")

        return {
            "id": poke_id,
            "name": name_cn,
            "name_en": name_en,
            "types": " / ".join(types),
            "height": f"{height}m",
            "weight": f"{weight}kg",
            "hp": stats.get("hp", 0),
            "atk": stats.get("attack", 0),
            "defense": stats.get("defense", 0),
            "speed": stats.get("speed", 0),
            "sprite": sprite,
        }
    except Exception as e:
        return {"name": "加载失败", "name_en": "", "types": "", "id": 0}
