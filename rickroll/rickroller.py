from ipaddress import ip_address
from socket import gethostbyname
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

__RICK_ROLL_URL__ = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

__REQUEST_HEADERS__ = headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/102.0.0.0 Safari/537.36"
    ),
}
__REQUEST_TIMEOUT_SECONDS__ = 10  # Reduced timeout for security


class RickRollError(Exception):
    def __init__(self, url: str, *args: object) -> None:
        super().__init__(*args)
        self.url = url


class RickRoller:
    @classmethod
    def rickroll(cls, url: str, rickroll_url=__RICK_ROLL_URL__, scroll_redirects_after=0) -> str:
        cls.__ensure_is_safe(url)
        soup = cls.__get_soup(url)

        cls.__absolutize(soup, url)
        cls.__insert_js(
            soup,
            rickroll_url=rickroll_url,
            scroll_redirects_after=scroll_redirects_after,
        )

        return str(soup)

    @staticmethod
    def __absolutize(soup, url):
        if soup.head is None:
            # some pages may lack the <head>
            # for example: https://html.spec.whatwg.org/multipage/semantics.html
            tag = soup.new_tag("head")
            soup.insert(0, soup.new_tag("head"))

        base = soup.head.find("base")
        if base is None:
            tag = soup.new_tag("base")
            tag.attrs["href"] = url
            soup.head.insert(0, tag)
        else:
            base.attrs["href"] = urljoin(url, base.attrs["href"])

    @staticmethod
    def __insert_js(soup, rickroll_url, scroll_redirects_after=0):
        # always redirect on touch or click event
        js = """
            function roll(e) {{
                if (e) {{ e.stopPropagation(); e.preventDefault(); }}
                window.location.href = "{}";
                return false;
            }}
            document.addEventListener("click", roll, true);
            document.addEventListener("touch", roll, true);
        """.format(  # noqa: UP032
            rickroll_url,
        )

        if scroll_redirects_after and scroll_redirects_after > 0:
            # if requested, also redirect after X scrolls (required a "scroll end" event)
            js += """
            function scrollStop(callback, refresh = 250) {
                let isScrolling;
                window.addEventListener('scroll', function (event) {
                    window.clearTimeout(isScrolling);
                    isScrolling = setTimeout(callback, refresh);
                }, false);
            }
            let numScrolls = 0;
            scrollStop(function() {
                if(++numScrolls >= %d) roll();
            });
            """ % (scroll_redirects_after,)

        tag = soup.new_tag("script")
        tag.attrs["type"] = "text/javascript"
        tag.string = (
            'document.addEventListener("DOMContentLoaded", function(event) {{ {} }});'.format(  # noqa: UP032
                js,
            )
        )

        if not soup.body:
            soup.insert(len(soup.contents), soup.new_tag("body"))

        soup.body.insert(len(soup.body.contents), tag)

    @staticmethod
    def __ensure_is_safe(url: str):
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        if hostname is None:
            raise RickRollError(url, f'Could not extract hostname from "{url}"')
        
        # Block localhost and local network references
        if hostname.lower() in ['localhost', '127.0.0.1', '::1', '0.0.0.0']:
            raise RickRollError(url, f"Access to localhost is not allowed: {hostname}")
        
        try:
            ip = gethostbyname(hostname)
            ip_obj = ip_address(ip)
            
            # Check for private IP ranges and other sensitive addresses
            if (ip_obj.is_private or ip_obj.is_loopback or 
                ip_obj.is_link_local or ip_obj.is_multicast or
                ip_obj.is_reserved or ip_obj.is_unspecified):
                raise RickRollError(url, f"{url} maps to a restricted IP address: {ip}")
            
            # Additional check for common cloud metadata IPs
            if ip == "169.254.169.254":  # AWS/GCP/Azure metadata service
                raise RickRollError(url, "Access to cloud metadata services is not allowed")
                
        except Exception as e:
            if isinstance(e, RickRollError):
                raise
            raise RickRollError(url, f"DNS resolution failed for {hostname}: {str(e)}")
            
        # Check for suspicious ports
        port = parsed_url.port
        if port is not None:
            # Block common internal service ports
            blocked_ports = {22, 23, 25, 53, 135, 139, 445, 1433, 1521, 3306, 3389, 5432, 6379, 9200, 27017}
            if port in blocked_ports:
                raise RickRollError(url, f"Access to port {port} is not allowed")

    @staticmethod
    def __get_soup(url: str) -> BeautifulSoup:
        response = requests.get(
            url,
            headers=__REQUEST_HEADERS__,
            timeout=__REQUEST_TIMEOUT_SECONDS__,
        )
        if response.status_code == 200:
            # Check response size to prevent memory attacks
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB limit
                raise RickRollError(url, "Response too large (maximum 50MB)")
            
            # Validate content type
            ctype = response.headers.get("Content-Type", "").lower()
            if "text/html" not in ctype and "application/xhtml" not in ctype:
                raise RickRollError(url, f'Only HTML pages are supported, got "{ctype}".')

            # Validate all URLs in redirect history
            for redirect_response in response.history:
                RickRoller.__ensure_is_safe(redirect_response.url)
            
            # Parse with security considerations
            try:
                return BeautifulSoup(response.content, "html.parser")
            except Exception as e:
                raise RickRollError(url, f"Failed to parse HTML content: {str(e)}")

        raise RickRollError(
            url,
            f"Error getting {url}: {response.status_code} {response.reason}",
        )
