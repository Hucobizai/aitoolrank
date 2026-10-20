
"""Prepare safe, reviewable content-enrichment suggestions for AI ToolRank.

Reads existing tools and writes a separate review file.
Never changes approved tool records or published pages.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "data" / "tools.json"
OUTPUT_PATH = ROOT / "data" / "enrichment_queue.json"

# Suggestions are intentionally conservative and category-based.
# They are starting points for human review, not verified product claims.
CATEGORY_SUGGESTIONS = {
    "AI Assistants": {
        "features": [
            "Answer questions and assist with everyday tasks",
            "Help draft and revise written content",
            "Support brainstorming and idea development",
        ],
        "best_for": [
            "Students and researchers",
            "Writers and content creators",
            "Professionals exploring AI assistants",
        ],
    },
    "AI Writing": {
        "features": [
            "Assist with drafting written content",
            "Suggest revisions and improvements",
            "Support content brainstorming",
        ],
        "best_for": [
            "Writers and editors",
            "Marketing professionals",
            "Content creators",
        ],
    },
    "AI Image Generation": {
        "features": [
            "Generate images from text prompts",
            "Explore visual concepts",
            "Support creative design workflows",
        ],
        "best_for": [
            "Designers and illustrators",
            "Content creators",
            "Marketing teams",
        ],
    },
}


def main():
    tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
    queue = []

    for tool in tools:
        if tool.get("status") != "approved":
            continue

        missing = [
            field
            for field in ("features", "best_for")
            if not tool.get(field)
        ]

        if not missing:
            continue

        category = tool.get("category", "")
        suggestions = CATEGORY_SUGGESTIONS.get(category, {})

        proposed = {
            field: suggestions[field]
            for field in missing
            if field in suggestions
        }

        queue.append({
            "id": tool["id"],
            "name": tool["name"],
            "category": category,
            "missing_fields": missing,
            "proposed": proposed,
            "review_status": "pending",
            "note": (
                "Category-based suggestions only. "
                "Verify each claim against the official provider "
                "before approving or publishing."
            ),
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(queue, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Tools reviewed: {len(tools)}")
    print(f"Listings needing enrichment: {len(queue)}")
    print(f"Review queue saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
