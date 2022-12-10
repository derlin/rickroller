from abc import ABC, abstractmethod
from typing import Self, Optional
from urllib.parse import quote, unquote
import random, string


class Persistence(ABC):
    supports_cleanup: bool

    @abstractmethod
    def create(self: Self, url: str) -> str:
        pass

    @abstractmethod
    def lookup(self: Self, slug: str) -> str:
        pass

    def teardown(self: Self, exception: Optional[Exception]):
        pass

    def cleanup(self: Self, **kwargs):
        pass

    def generate_slug(self: Self) -> str:
        return "".join(random.choice(string.hexdigits) for _ in range(15))


class NoPersistence(Persistence):
    supports_cleanup = False

    def create(self: Self, url: str) -> str:
        return quote(url, safe="")

    def lookup(self: Self, slug: str) -> str:
        return unquote(slug)
