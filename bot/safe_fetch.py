"""Safe official-website retrieval for AI ToolRank.

Network retrieval remains disabled until security testing.
"""

from urllib.parse import urlsplit
import ipaddress
import socket
import http.client
import ssl
from html.parser import HTMLParser
from urllib.parse import urljoin
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
def create_verified_connection(url):
    """Create an HTTPS connection using a validated public IP."""
    verified_ips = get_verified_public_ips(url)

    if not verified_ips:
        return None

    hostname = urlsplit(url).hostname

    return PinnedHTTPSConnection(
        hostname,
        verified_ips[0],
    )


def fetch_official_page(url):
    """Safely retrieve readable HTML from an official website."""
    connection = None

    try:
        if not is_allowed_url(url):
            return None

        connection = create_verified_connection(url)
        if connection is None:
            return None

        parsed = urlsplit(url)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        connection.request(
            "GET",
            path,
            headers={
                "User-Agent": "AIToolRankResearch/1.0",
                "Accept": "text/html",
                "Connection": "close",
            },
        )

        response = connection.getresponse()

        if response.status != 200:
            print("Website returned HTTP status:", response.status)
            return None

        content_type = response.getheader("Content-Type", "")
        if not content_type.lower().split(";")[0].strip() == "text/html":
            return None

        max_bytes = 1024 * 1024
        content = response.read(max_bytes + 1)

        if len(content) > max_bytes:
            return None

        html = content.decode("utf-8", errors="replace")
        return extract_website_text(html)

    except (OSError, ValueError, TimeoutError, http.client.HTTPException):
        return None

    finally:
        if connection is not None:
            connection.close()

class WebsiteTextExtractor(HTMLParser):
    """Extract readable text from website HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0
        self.skip_tags = {
            "script", "style", "noscript",
            "nav", "footer", "header",
            "svg", "form",
        }

    def handle_starttag(self, tag, attrs):
        if self.skip_depth:
            self.skip_depth += 1
        elif tag in self.skip_tags:
            self.skip_depth = 1

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)


def extract_website_text(html):
    """Convert HTML into readable research text."""
    parser = WebsiteTextExtractor()
    parser.feed(html)
    return " ".join(parser.parts)
