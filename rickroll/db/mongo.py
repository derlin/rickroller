from datetime import datetime, timedelta
from typing import Self, Optional

from pymongo import MongoClient

from .persistence import Persistence


class MongoPersistence(Persistence):
    __COLL__ = "urls"

    __slug = "_id"
    __url = "url"
    __client_ip = "client_ip"
    __last_accessed = "ts"

    supports_cleanup = True

    def __init__(self: Self, app, max_urls_per_ip, connection_uri):
        super().__init__(app, max_urls_per_ip)
        self.client = MongoClient(connection_uri)
        self.coll = self.client.get_database()[self.__COLL__]

    def _get(self: Self, url: str) -> Optional[str]:
        result = self.coll.find_one({self.__url: url})
        return result[self.__slug] if result else None

    def _create(self: Self, url: str, client_ip: str) -> str:
        tiny = {
            self.__slug: self.generate_slug(),
            self.__url: url,
            self.__client_ip: client_ip,
            self.__last_accessed: self.now(),
        }
        self.coll.insert_one(tiny)
        self.app.logger.debug(f"Inserted {tiny} in MongoDB.")
        return tiny[self.__slug]

    def lookup(self: Self, slug: str) -> str:
        tiny = self.coll.find_one({self.__slug: slug})
        if tiny is None:
            raise Exception(f'Slug "{slug}" in invalid or has expired')

        self.coll.update_one(
            {self.__slug: slug},
            {"$set": {self.__last_accessed: self.now()}},
        )
        return tiny["url"]

    def urls_per_ip(self: Self, ip: str) -> int:
        return self.coll.count_documents({self.__client_ip: ip})

    def cleanup(self: Self, retention: timedelta):
        limit = self.now() - retention
        query = {self.__last_accessed: {"$lte": limit}}
        if (cnt := self.coll.delete_many(query).deleted_count) > 0:
            self.app.logger.info(f"Removed {cnt} record(s) from database.")

    def teardown(self: Self, exception: Optional[Exception]):
        pass
