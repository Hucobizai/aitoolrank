"""Tests for AI ToolRank's safe URL validation."""

from safe_fetch import is_allowed_url, has_public_dns, fetch_official_page


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
    print("\nTesting DNS security...")

    assert has_public_dns("https://localhost/") is False
    print("PASS: localhost rejected")

    assert has_public_dns("https://127.0.0.1/") is False
    print("PASS: loopback IP rejected")

    assert has_public_dns("https://192.168.1.1/") is False
    print("PASS: private IP rejected")

    assert has_public_dns("https://example.local/") is False
    print("PASS: local domain rejected")

    assert fetch_official_page("https://localhost/") is None
    print("PASS: localhost retrieval blocked")

    print("All DNS security tests passed.")

if __name__ == "__main__":
    main()
