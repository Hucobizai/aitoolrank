"""Safe official-website retrieval for AI ToolRank.

Network retrieval remains disabled until security testing.
"""

from urllib.parse import urlsplit


def is_allowed_url(url):
    """Accept only standard HTTPS website URLs."""
    if not isinstance(url, str):
        return False

    try:
        parsed = urlsplit(url)

        return (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.port in (None, 443)
            and parsed.username is None
            and parsed.password is None
            and not parsed.hostname.endswith(".local")
        )
    except ValueError:
        return False


def fetch_official_page(url):
    """Return extracted website text, or None when unavailable."""
    if not is_allowed_url(url):
        return None

    # Network retrieval is intentionally disabled.
    return None
