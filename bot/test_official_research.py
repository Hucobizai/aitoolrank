"""Read-only test of official AI tool website research."""

from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from html.parser import HTMLParser
import re
import json

class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_stack = []
        self.content_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "nav", "footer"):
            self.skip_stack.append(tag)

        if tag in ("main", "article"):
            self.content_depth += 1

    def handle_endtag(self, tag):
        if self.skip_stack and self.skip_stack[-1] == tag:
            self.skip_stack.pop()

        if tag in ("main", "article"):
            self.content_depth = max(0, self.content_depth - 1)

    def handle_data(self, data):
        if self.skip_stack:
            return

        if self.content_depth > 0:
            value = re.sub(r"\s+", " ", data).strip()

            if value:
                self.parts.append(value)

def main():
    url = "https://cursor.com/"
    parsed = urlparse(url)

    if parsed.scheme != "https" or parsed.hostname != "cursor.com":
        raise ValueError("Unexpected research URL")

    request = Request(
        url,
        headers={"User-Agent": "AIToolRankResearch/0.1"}
    )

    opener = build_opener(NoRedirects())

    print("Research test configured for:", url)
    print("Attempting read-only retrieval from Cursor")

    try:
        with opener.open(request, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "")

            if "text/html" not in content_type.lower():
                print("Website did not return HTML")
                return

            html = response.read(100_000).decode(
                "utf-8", errors="replace"
            )

        parser = TextExtractor()
        parser.feed(html)

        useful_parts = [
            part for part in parser.parts
            if len(part.split()) >= 5
        ]

        text = "\n".join(useful_parts)

        print("Website:", url)
        print("Characters extracted:", len(text))
        print("Preview:", text[:1000])

        keywords = ("agent", "code", "development", "software")

        evidence_records = []

        for part in useful_parts:
            if any(word in part.lower() for word in keywords):
                strong_phrases = (
                    "agents turn",
                    "coding agent",
                    "accelerate development",
                    "handing off tasks"
                )

                relevance = (
                    "high"
                    if any(
                        phrase in part.lower()
                        for phrase in strong_phrases
                    )
                    else "low"
                )

                evidence_records.append({
                    "tool": "Cursor",
                    "source_url": url,
                    "evidence": part[:250],
                    "relevance": relevance,
                    "review_status": "pending"
                })

        print("\nStructured evidence records:")
        print(json.dumps(evidence_records, indent=2))
        feature_suggestions = []

        for record in evidence_records:
            if record["relevance"] != "high":
                continue

            evidence = record["evidence"].lower()

            if "coding agent" in evidence:
                suggestion = "AI coding agent for software development"
            elif "agents turn" in evidence:
                suggestion = "AI agents that help turn ideas into code"
            elif "handing off tasks" in evidence:
                suggestion = "Delegate development tasks to AI agents"
            else:
                continue

            feature_suggestions.append({
                "tool": record["tool"],
                "suggested_feature": suggestion,
                "source_url": record["source_url"],
                "supporting_evidence": record["evidence"],
                "review_status": "pending"
            })

        print("\nDraft feature suggestions:")
        print(json.dumps(feature_suggestions, indent=2))
    except Exception as error:
        print("Website retrieval failed:", type(error).__name__)


if __name__ == "__main__":
    main()
