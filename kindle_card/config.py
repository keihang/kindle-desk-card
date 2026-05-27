import yaml
from pathlib import Path


def load(path: str = "config.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
