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


class RickRoller:
    @classmethod
    def rickroll(cls, url: str) -> str:
        cls.__ensure_is_safe(url)
        soup = cls.__get_soup(url)

        args = [soup, url]

        cls.__absolutize(*args)
        cls.__insert_js(*args)

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
    def __insert_js(soup, *args):
        js = (
            """
        document.addEventListener("DOMContentLoaded", function(event) {
            document.addEventListener("click", e => {
                e.stopPropagation();
                e.preventDefault();
                window.location = "%s"
            }, true);
        });
        """
            % __RICK_ROLL_URL__
        )

        tag = soup.new_tag("script")
        tag.attrs["type"] = "text/javascript"
        tag.string = js

        soup.body.insert(len(soup.body.contents), tag)

    @staticmethod
    def __ensure_is_safe(url: str):
        hostname = urlparse(url).hostname
        if hostname is None:
            raise Exception(f'Could not extract hostname from "{url}"')
        ip = gethostbyname(hostname)

        if ip is None or ip_address(ip).is_private:
            raise Exception(f"{url} maps to an unknown or private ip address: {ip}.")

    @staticmethod
    def __get_soup(url: str) -> BeautifulSoup:
        response = requests.get(
            url, headers=__REQUEST_HEADERS__, timeout=__REQUEST_TIMEOUT_SECONDS__
        )
        if response.status_code == 200:
            [RickRoller.__ensure_is_safe(r.url) for r in response.history]
            return BeautifulSoup(response.text, "html.parser")

        raise Exception(
            f"Error getting {url}: {response.status_code} {response.reason}"
        )
