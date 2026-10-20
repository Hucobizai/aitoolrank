
"""Prepare safe, reviewable content-enrichment suggestions for AI ToolRank.

Reads existing tools and writes a separate review file.
Never changes approved tool records or published pages.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "data" / "tools.json"
OUTPUT_PATH = ROOT / "data" / "enrichment_queue.json"

# Suggestions are intentionally conservative and category-based.
# They are starting points for human review, not verified product claims.

CATEGORY_SUGGESTIONS = {
    "AI Assistants": {
        "features": [
            "Answer questions and help explain information",
            "Assist with drafting and editing content",
            "Support brainstorming and research tasks",
        ],
        "best_for": [
            "Writers and content creators",
            "Students and researchers",
            "Business professionals",
        ],
    },
    "AI Agents": {
        "features": [
            "Support AI-powered automation workflows",
            "Help build or run AI-driven applications",
            "Work with AI models or agent-based systems",
        ],
        "best_for": [
            "AI developers",
            "Automation specialists",
            "Businesses exploring AI workflows",
        ],
    },
    "Vibe Coding": {
        "features": [
            "Assist with software development tasks",
            "Support AI-powered code creation or editing",
            "Help streamline application development",
        ],
        "best_for": [
            "Software developers",
            "Entrepreneurs building applications",
            "People exploring AI-assisted coding",
        ],
    },
    "AI Video": {
        "features": [
            "Support AI-powered video creation workflows",
            "Assist with generating or editing visual content",
            "Help produce creative media projects",
        ],
        "best_for": [
            "Video creators",
            "Marketing professionals",
            "Content production teams",
        ],
    },
    "AI Audio": {
        "features": [
            "Support AI-powered audio creation",
            "Assist with producing or editing audio content",
            "Help streamline audio production workflows",
        ],
        "best_for": [
            "Podcasters and audio creators",
            "Music and media producers",
            "Content creators",
        ],
    },
    "AI Research": {
        "features": [
            "Help explore and organize information",
            "Support research and information analysis",
            "Assist with summarizing research materials",
        ],
        "best_for": [
            "Students and researchers",
            "Business analysts",
            "Professionals working with information",
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
