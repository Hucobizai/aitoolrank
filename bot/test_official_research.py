"""Read-only test of official AI tool website research."""

from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from html.parser import HTMLParser
import re


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

        text = "\n".join(parser.parts)

        print("Website:", url)
        print("Characters extracted:", len(text))
        print("Preview:", text[:1000])

    except Exception as error:
        print("Website retrieval failed:", type(error).__name__)


if __name__ == "__main__":
    main()
