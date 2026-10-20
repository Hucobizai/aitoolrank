
"""Generate SEO-friendly pages for approved AI ToolRank listings."""

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "tools.json"
OUTPUT = ROOT / "docs" / "tools"
BASE_URL = "https://hucobizai.github.io/aitoolrank"


def escape(value):
    return html.escape(str(value or ""), quote=True)


def generate_page(tool):
    name = str(tool["name"])
    slug = str(tool["id"])
    category = str(tool["category"])
    summary = str(tool["summary"])
    pricing = str(tool.get("pricing") or "Check official pricing.")
    website = str(tool["url"])
    pricing_url = str(tool.get("pricing_url") or website)
    features = tool.get("features", [])
    features_html = ""

    if isinstance(features, list) and features:
        features_html = (
            "<h2>Key Features</h2>\n<ul>\n"
            + "\n".join(
                f"<li>{escape(feature)}</li>"
                for feature in features
                if isinstance(feature, str) and feature.strip()
            )
            + "\n</ul>"
        )

    canonical = f"{BASE_URL}tools/{quote(slug)}/"
    title = f"{name} - Features, Pricing & Overview | AI ToolRank"
    description = f"Explore {name}: {summary}"[:155]

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{escape(canonical)}">
  <link rel="stylesheet" href="../../style.css">
</head>
<body>
  <header>
    <div class="wrap nav">
      <a class="brand" href="../../">✦ AI ToolRank</a>
      <a href="../../#about">How we evaluate</a>
    </div>
  </header>

  <main class="wrap">
    <section class="hero">
      <span class="eyebrow">{escape(category)}</span>
      <h1>{escape(name)}</h1>
      <p>{escape(summary)}</p>
    </section>

    <section class="section">
      <h2>About {escape(name)}</h2>
      <p>{escape(summary)}</p>
      <h2>Best For</h2>
<p>Recommended for: {escape(", ".join(tool.get("best_for") or [tag.replace("-", " ").title() for tag in tool.get("tags", []) if isinstance(tag, str)]))}</p>      {features_html}
      <h2>Pricing</h2>
      <p>{escape(pricing)}</p>

      <p>
        <a href="{escape(pricing_url)}"
           target="_blank" rel="noopener noreferrer">
          View official pricing ↗
        </a>
      </p>

      <h2>Explore {escape(name)}</h2>
      <p>
        <a href="{escape(website)}"
           target="_blank" rel="noopener noreferrer">
          Visit official website ↗
        </a>
      </p>

      <p class="muted fine">
        Product details are based on published descriptions.
        Features and prices may change. Verify with the provider.
      </p>
    </section>

    <section class="section">
      <a href="../../">← Browse all AI tools</a>
    </section>
  </main>
</body>
</html>
"""


def main():
    tools = json.loads(SOURCE.read_text(encoding="utf-8"))
    approved = [t for t in tools if t.get("status") == "approved"]

    OUTPUT.mkdir(parents=True, exist_ok=True)

      # Remove generated pages for tools that are no longer approved.
    approved_ids = {str(tool["id"]) for tool in approved}

    for page_dir in OUTPUT.iterdir():
        if page_dir.is_dir() and page_dir.name not in approved_ids:
            index_file = page_dir / "index.html"
            if index_file.exists():
                index_file.unlink()
                page_dir.rmdir()

    count = 0

    for tool in approved:
        slug = str(tool["id"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Unsafe tool ID: {slug}")

        page_dir = OUTPUT / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            generate_page(tool), encoding="utf-8"
        )
        count += 1

        # Generate a sitemap for the homepage and approved tool pages.
    urls = [f"{BASE_URL}/"]

    for tool in approved:
        slug = str(tool["id"])
        urls.append(f"{BASE_URL}/tools/{quote(slug)}/")

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(
            f"  <url><loc>{html.escape(url)}</loc></url>\n"
            for url in urls
        )
        + "</urlset>\n"
    )

    (ROOT / "docs" / "sitemap.xml").write_text(
        sitemap, encoding="utf-8"
    )

    print(f"Generated {count} approved AI tool pages.")
    print(f"Generated sitemap with {len(urls)} URLs.")


if __name__ == "__main__":
    main()
