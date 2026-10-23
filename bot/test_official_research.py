"""Read-only test of official AI tool website research."""
from safe_fetch import fetch_official_page
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

    print("Research test configured for:", url)
    print("Attempting safe read-only retrieval from Cursor")

    try:
        text = fetch_official_page(url)

        if not text:
            print("Website retrieval unavailable")
            return

        useful_parts = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if len(sentence.split()) >= 5
        ]

        text = "\n".join(useful_parts)
        print("Website:", url)
        print("Characters extracted:", len(text))
        print("Preview:", text[:1000])

        keywords = ("agent", "code", "development", "software")

        evidence_records = []
        seen_evidence = set()
        for part in useful_parts:
            if "This element contains an interactive demo" in part:
                continue

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
                if part in seen_evidence:
                    continue

                seen_evidence.add(part)
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
        seen_features = set()
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
            if suggestion in seen_features:
                continue

            seen_features.add(suggestion)
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
