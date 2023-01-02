import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from socket import gethostbyname
from ipaddress import ip_address

__RICK_ROLL_URL__ = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

__REQUEST_HEADERS__ = headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}
__REQUEST_TIMEOUT_SECONDS__ = 30


class RickRollException(Exception):
    def __init__(self, url: str, *args: object) -> None:
        super().__init__(*args)
        self.url = url


class RickRoller:
    @classmethod
    def rickroll(
        cls, url: str, rickroll_url=__RICK_ROLL_URL__, scroll_redirects_after=0
    ) -> str:
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
            function roll(e) {
                if (e) { e.stopPropagation(); e.preventDefault(); }
                window.location.href = "%s";
                return false;
            }
            document.addEventListener("click", roll, true);
            document.addEventListener("touch", roll, true);
        """ % (
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
            """ % (
                scroll_redirects_after,
            )

        tag = soup.new_tag("script")
        tag.attrs["type"] = "text/javascript"
        tag.string = (
            'document.addEventListener("DOMContentLoaded", function(event) { %s });'
            % (js,)
        )

        if not soup.body:
            soup.insert(len(soup.contents), soup.new_tag("body"))

        soup.body.insert(len(soup.body.contents), tag)

    @staticmethod
    def __ensure_is_safe(url: str):
        hostname = urlparse(url).hostname
        if hostname is None:
            raise RickRollException(url, f'Could not extract hostname from "{url}"')
        ip = gethostbyname(hostname)

        if ip is None or ip_address(ip).is_private:
            raise RickRollException(
                url, f"{url} maps to an unknown or private ip address: {ip}."
            )

    @staticmethod
    def __get_soup(url: str) -> BeautifulSoup:
        response = requests.get(
            url, headers=__REQUEST_HEADERS__, timeout=__REQUEST_TIMEOUT_SECONDS__
        )
        if response.status_code == 200:
            if "text/html" not in (ctype := response.headers["Content-Type"]):
                raise RickRollException(
                    url, f'Only HTML pages are supported, got "{ctype}".'
                )

            [RickRoller.__ensure_is_safe(r.url) for r in response.history]
            return BeautifulSoup(response.content, "html.parser")

        raise RickRollException(
            url, f"Error getting {url}: {response.status_code} {response.reason}"
        )
