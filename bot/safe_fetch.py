"""Safe official-website retrieval for AI ToolRank.

Network retrieval remains disabled until security testing.
"""

from urllib.parse import urlsplit
import ipaddress
import socket
import http.client
import ssl
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

def has_public_dns(url):
    """Check that all resolved IP addresses are public."""
    if not is_allowed_url(url):
        return False

    try:
        hostname = urlsplit(url).hostname

        addresses = socket.getaddrinfo(
            hostname,
            443,
            type=socket.SOCK_STREAM,
        )

        if not addresses:
            return False

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return False

        return True

    except (OSError, ValueError):
        return False
def get_verified_public_ips(url):
    """Return public IP addresses, or an empty list if validation fails."""
    if not is_allowed_url(url):
        return []

    try:
        hostname = urlsplit(url).hostname

        addresses = socket.getaddrinfo(
            hostname,
            443,
            type=socket.SOCK_STREAM,
        )

        if not addresses:
            return []

        verified_ips = []

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return []

            ip_text = str(ip)

            if ip_text not in verified_ips:
                verified_ips.append(ip_text)

        return verified_ips

    except (OSError, ValueError):
        return []
class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to a specific IP while verifying the original hostname."""

    def __init__(self, hostname, verified_ip, timeout=10):
        super().__init__(
            hostname,
            port=443,
            timeout=timeout,
            context=ssl.create_default_context(),
        )
        self.verified_ip = verified_ip

    def connect(self):
        raw_socket = socket.create_connection(
            (self.verified_ip, self.port),
            self.timeout,
        )

        try:
            self.sock = self._context.wrap_socket(
                raw_socket,
                server_hostname=self.host,
            )
        except Exception:
            raw_socket.close()
            raise
def fetch_official_page(url):
    """Return extracted website text, or None when unavailable."""
    verified_ips = get_verified_public_ips(url)

    if not verified_ips:
        return None

    # Network retrieval is intentionally disabled.
    return None
