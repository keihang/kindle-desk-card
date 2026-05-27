import subprocess
import json
import re


def _fetch_from_doc(doc_url: str) -> dict:
    """Fetch tasks from a Feishu document."""
    try:
        result = subprocess.run(
            ["lark-cli", "docs", "+fetch", "--api-version", "v2", "--doc", doc_url, "--format", "json"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return {"items": []}

        resp = json.loads(result.stdout)
        if not resp.get("ok"):
            return {"items": []}

        # Parse document content for task items
        content = resp.get("data", {}).get("content", "")
        items = []
        for line in content.split("\n"):
            line = line.strip()
            # Match lines starting with - [ ] or - [x] or numbered lists
            if re.match(r"^-\s*\[[ x]\]", line):
                title = re.sub(r"^-\s*\[[ x]\]\s*", "", line)
                if title:
                    items.append({"title": title, "due": "", "status": "todo"})
            elif re.match(r"^\d+[\.\)]\s*", line):
                title = re.sub(r"^\d+[\.\)]\s*", "", line)
                if title:
                    items.append({"title": title, "due": "", "status": "todo"})
            elif line.startswith("- ") or line.startswith("· "):
                title = line[2:].strip()
                if title:
                    items.append({"title": title, "due": "", "status": "todo"})

        return {"items": items[:10]}
    except Exception:
        return {"items": []}


def _fetch_from_tasks() -> dict:
    """Fetch tasks from Feishu task API."""
    try:
        result = subprocess.run(
            ["lark-cli", "task", "+get-my-tasks", "--format", "json", "--complete=false"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return {"items": []}

        resp = json.loads(result.stdout)
        tasks = resp.get("data", {}).get("items") or []
        items = []
        for t in tasks[:10]:
            items.append({
                "title": t.get("summary", t.get("title", "")),
                "due": t.get("due", {}).get("date", "") if t.get("due") else "",
                "status": t.get("status", ""),
            })
        return {"items": items}
    except Exception:
        return {"items": []}


def fetch(config: dict = None) -> dict:
    """Fetch tasks. Default: Feishu task API. Set doc_url in config to use document mode."""
    if config and config.get("doc_url"):
        return _fetch_from_doc(config["doc_url"])
    return _fetch_from_tasks()
