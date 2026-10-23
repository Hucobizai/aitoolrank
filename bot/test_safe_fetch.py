"""Tests for AI ToolRank's safe URL validation."""
from unittest.mock import patch, MagicMock
from safe_fetch import (
    is_allowed_url,
    has_public_dns,
    get_verified_public_ips,
    create_verified_connection,
    fetch_official_page,
    PinnedHTTPSConnection,
    extract_website_text,
)


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
    print("\nTesting pinned HTTPS configuration...")

    connection = PinnedHTTPSConnection(
        "cursor.com",
        "1.1.1.1",
    )

    assert connection.host == "cursor.com"
    assert connection.verified_ip == "1.1.1.1"
    assert connection.port == 443
    assert connection._context.verify_mode == 2
    assert connection._context.check_hostname is True

    connection.close()

    print("PASS: HTTPS connection configuration")
    print("\nTesting pinned HTTPS connection behavior...")

    with patch("safe_fetch.socket.create_connection") as mock_connect:
        with patch.object(connection._context, "wrap_socket") as mock_tls:
            mock_connect.return_value = MagicMock()
            mock_tls.return_value = MagicMock()

            connection.connect()

            mock_connect.assert_called_once_with(
                ("1.1.1.1", 443),
                10,
            )

            assert mock_tls.call_args.kwargs["server_hostname"] == "cursor.com"

    connection.close()

    print("PASS: Pinned IP and TLS hostname verification")
    print("\nTesting verified public IP retrieval...")

    fake_dns = [
        (2, 1, 6, "", ("8.8.8.8", 443)),
        (2, 1, 6, "", ("1.1.1.1", 443)),
    ]

    with patch("safe_fetch.socket.getaddrinfo", return_value=fake_dns):
        result = get_verified_public_ips("https://cursor.com/")
        assert result == ["8.8.8.8", "1.1.1.1"]

    print("PASS: Public IP addresses accepted")

    private_dns = [
        (2, 1, 6, "", ("192.168.1.1", 443)),
    ]

    with patch("safe_fetch.socket.getaddrinfo", return_value=private_dns):
        result = get_verified_public_ips("https://cursor.com/")
        assert result == []

    print("PASS: Private IP addresses rejected")
    print("\nTesting retrieval with validated IP results...")

    with patch(
        "safe_fetch.get_verified_public_ips",
        return_value=["8.8.8.8"],
    ) as mock_verified:
        result = fetch_official_page("https://cursor.com/")

        assert result is None
        mock_verified.assert_called_once_with("https://cursor.com/")

    print("PASS: Retrieval uses validated IP results")
    print("\nTesting that network retrieval stays disabled...")

    with patch(
        "safe_fetch.get_verified_public_ips",
        return_value=["8.8.8.8"],
    ):
        with patch.object(PinnedHTTPSConnection, "connect") as mock_connect:
            result = fetch_official_page("https://cursor.com/")

            assert result is None
            mock_connect.assert_not_called()

    print("PASS: Network retrieval remains disabled")
    print("\nTesting verified HTTPS connection helper...")

    with patch(
        "safe_fetch.get_verified_public_ips",
        return_value=["8.8.8.8"],
    ) as mock_verified:
        connection = create_verified_connection("https://cursor.com/")

        assert isinstance(connection, PinnedHTTPSConnection)
        assert connection.host == "cursor.com"
        assert connection.verified_ip == "8.8.8.8"
        mock_verified.assert_called_once_with("https://cursor.com/")

        connection.close()

    print("PASS: Verified HTTPS connection helper")
    print("\nTesting connection rejection without verified IPs...")

    with patch(
        "safe_fetch.get_verified_public_ips",
        return_value=[],
    ) as mock_verified:
        connection = create_verified_connection("https://cursor.com/")

        assert connection is None
        mock_verified.assert_called_once_with("https://cursor.com/")

    print("PASS: Connection rejected without verified IPs")
    print("\nTesting HTTPS connection failure handling...")

    connection = PinnedHTTPSConnection("cursor.com", "8.8.8.8")

    with patch(
        "safe_fetch.socket.create_connection",
        side_effect=OSError("Simulated connection failure"),
    ):
        try:
            connection.connect()
        except OSError:
            print("PASS: HTTPS connection failure detected")
        else:
            raise AssertionError("Connection failure was not detected")
        finally:
            connection.close()
    print("\nTesting website retrieval error handling...")

    with patch(
        "safe_fetch.get_verified_public_ips",
        side_effect=OSError("Simulated DNS failure"),
    ):
        result = fetch_official_page("https://cursor.com/")

        assert result is None

    print("PASS: Website retrieval handles DNS errors safely")
    print("\nTesting timeout and validation errors...")

    for error in (
        TimeoutError("Simulated timeout"),
        ValueError("Simulated validation error"),
    ):
        with patch(
            "safe_fetch.get_verified_public_ips",
            side_effect=error,
        ):
            result = fetch_official_page("https://cursor.com/")
            assert result is None

    print("PASS: Timeout and validation errors handled safely")
    print("\nTesting HTML text extraction...")

    sample_html = """
    <html>
      <head>
        <title>Cursor AI</title>
        <script>ignore_script()</script>
      </head>
      <body>
        <nav>Navigation Menu</nav>
        <main>
          <h1>Cursor AI Coding Assistant</h1>
          <p>Build software with AI agents.</p>
        </main>
        <footer>Footer Links</footer>
      </body>
    </html>
    """

    extracted = extract_website_text(sample_html)

    assert "Cursor AI Coding Assistant" in extracted
    assert "Build software with AI agents." in extracted
    assert "ignore_script" not in extracted
    assert "Navigation Menu" not in extracted
    assert "Footer Links" not in extracted

    print("PASS: HTML text extraction")
if __name__ == "__main__":
    main()
