import pytest
import contextlib

from typing import List
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

from rickroll.rickroller import RickRoller, RickRollException, __RICK_ROLL_URL__

UrlHolder = namedtuple("Request", ["url"])
some_url = "https://example.com"


@contextlib.contextmanager
def request_faker(
    body: str = "<html><body></body></html>",
    history: List[str] = [],
    status_code: int = 200,
    content_type="text/html",
):
    def mock_get(url: str, *args, **kwargs):
        fake_response = requests.Response()
        fake_response.url = url
        fake_response.status_code = status_code
        fake_response._content = body.encode("utf-8")
        fake_response.history = [UrlHolder(u) for u in history]
        fake_response.headers["Content-Type"] = content_type
        return fake_response

    with pytest.MonkeyPatch.context() as mk:
        original_get = requests.get
        mk.setattr(requests, "get", mock_get)
        yield requests
        mk.setattr(requests, "get", original_get)


def assert_is_rickrolled(url: str, **kwargs):
    result = RickRoller.rickroll(url, **kwargs)
    assert __RICK_ROLL_URL__ in result
    assert "function roll(" in result
    return result

def assert_fails(url: str, exception_message: str):
    with pytest.raises(RickRollException, match=exception_message):
        RickRoller.rickroll(url)

def test_scroll():
    for n in [-1, 0, None]:
        result = assert_is_rickrolled(some_url, scroll_redirects_after=n)
        assert "function scrollStop(" not in result
    for n in [1, 5, 100]:
        result = assert_is_rickrolled(some_url, scroll_redirects_after=n)
        assert "function scrollStop(" in result
        assert f"++numScrolls >= {n}" in result

def test_custom_rickroll_url():
    custom_rickroll_url = "<CUSTOM_RICKROLL_URL>"
    result = RickRoller.rickroll(some_url, rickroll_url=custom_rickroll_url)
    assert custom_rickroll_url in result
    assert __RICK_ROLL_URL__ not in result

def test_error():
    for status in [500, 401, 209]:
        with request_faker(status_code=status):
            assert_fails(some_url, f"Error getting {some_url}: {status}.*")


def test_private_hosts():
    expected_error = ".* maps to an unknown or private ip address.*"

    assert_fails("https://10.10.0.40:543/test", expected_error)

    with request_faker(history=["https://github.com", "https://gitlab.com"]):
        assert_is_rickrolled("https://example.com")

    with request_faker(history=["https://github.com", "http://127.0.0.1/test"]):
        assert_fails("https://example.com", expected_error)


def test_ctype():
    invalid_content_types = ["image/png", "application/vnd.ms-excel"]
    for ctype in invalid_content_types:
        with request_faker(content_type=ctype):
            assert_fails(some_url, "Only HTML pages are supported.*")

    valid_ctypes = ["text/html; charset=utf-8", "text/html"]
    for ctype in valid_ctypes:
        with request_faker(content_type=ctype):
            assert_is_rickrolled(some_url)


def test_absolutize():
    def assert_base_url(body, url):
        soup = BeautifulSoup(body, "html.parser")
        assert soup.head is not None
        base = soup.head.find("base")
        assert base is not None
        assert base.attrs["href"] == url

    with request_faker(body="<html></html>"):
        assert_base_url(RickRoller.rickroll(some_url), some_url)

    base_url = "http://example.com/folder/file.html"
    base_expected = [
        (base_url, base_url),
        ("../other", "http://example.com/other"),
        ("file2.html", "http://example.com/folder/file2.html"),
    ]

    for (base, expected) in base_expected:
        with request_faker(body=f'<html><head><base href="{base}"/></head></html>'):
            response_body = assert_is_rickrolled(base_url)
            assert_base_url(response_body, expected)
