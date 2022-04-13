import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


__RICK_ROLL_URL__ = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


class RickRoller:
    @classmethod
    def rickroll(self, url: str) -> str:
        soup = self.__get_soup(url)

        args = [soup, url]
        self.__absolutize("link", "href", *args)
        self.__absolutize("script", "src", *args)
        self.__absolutize("img", "src", *args)

        self.__fix_srcset(*args)

        self.__insert_js(*args)

        return str(soup)

    @staticmethod
    def __absolutize(tagname, attr, soup, url, *args):
        for elt in soup.find_all(tagname, **{attr: True}):
            elt.attrs[attr] = urljoin(url, elt.attrs[attr])

    @staticmethod
    def __fix_srcset(soup, url, *args):
        # for responsive images
        # e.g. "/static/563761cc22ded851baff4921ecc27649/e4a55/python-url-decode.jpg 256w, /static/563761cc22ded851baff4921ecc27649/36dd4/python-url-decode.jpg 512w, /static/563761cc22ded851baff4921ecc27649/72e01/python-url-decode.jpg 1024w, /static/563761cc22ded851baff4921ecc27649/ac99c/python-url-decode.jpg 1536w, /static/563761cc22ded851baff4921ecc27649/0f98f/python-url-decode.jpg 1920w"
        for elt in soup.find_all("img", srcset=True):
            srcset = elt.attrs["srcset"]

            transformed = []
            for entry in re.split(" *, *", srcset):
                items = re.split(" +", entry)
                transformed.append(" ".join([urljoin(url, items[0])] + items[1:]))

            elt.attrs["srcset"] = ",".join(transformed)

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

        print(js)
        soup.body.insert(len(soup.body.contents), tag)

    @staticmethod
    def __get_soup(url: str) -> BeautifulSoup:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                f"Error getting {url}: {response.status_code} {response.reason}"
            )
        return BeautifulSoup(response.text, "html.parser")
