"""Tests for AI ToolRank's safe URL validation."""

from safe_fetch import is_allowed_url, fetch_official_page


def main():
    test_cases = [
        ("https://cursor.com/", True),
        ("http://cursor.com/", False),
        ("https://localhost/", True),
        ("https://example.local/", False),
        ("https://user:pass@example.com/", False),
        ("https://example.com:8080/", False),
        ("not-a-url", False),
    ]

    for url, expected in test_cases:
        actual = is_allowed_url(url)
        assert actual == expected, (
            f"FAILED: {url} — expected {expected}, got {actual}"
        )
        print(f"PASS: {url}")

    print("All URL validation tests passed.")


if __name__ == "__main__":
    main()
