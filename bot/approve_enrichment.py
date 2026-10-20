
"""Apply explicitly approved enrichment suggestions to existing tools."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "data" / "tools.json"
QUEUE_PATH = ROOT / "data" / "enrichment_queue.json"

ALLOWED_FIELDS = ("features", "best_for")


def main():
    tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    approved = {
        item["id"]: item
        for item in queue
        if item.get("review_status") == "approved"
        and isinstance(item.get("id"), str)
    }

    updated = 0

    for tool in tools:
        item = approved.get(tool.get("id"))

        if item is None or tool.get("status") != "approved":
            continue

        proposed = item.get("proposed", {})
        if not isinstance(proposed, dict):
            continue

        changed = False

        for field in ALLOWED_FIELDS:
            values = proposed.get(field)

            if (
                not tool.get(field)
                and isinstance(values, list)
                and values
                and all(isinstance(v, str) and v.strip() for v in values)
            ):
                tool[field] = values
                changed = True

        if changed:
            updated += 1

    if updated:
        TOOLS_PATH.write_text(
            json.dumps(tools, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(f"Tools updated: {updated}")


if __name__ == "__main__":
    main()
