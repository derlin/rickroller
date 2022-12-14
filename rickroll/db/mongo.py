from datetime import datetime, timedelta
from typing import Self, Optional

from pymongo import MongoClient

from .persistence import Persistence


class MongoPersistence(Persistence):
    __COLL__ = "urls"

    __slug = "_id"
    __url = "url"
    __last_accessed = "ts"

    supports_cleanup = True

    def __init__(self: Self, app, connection_uri):
        self.app = app
        self.client = MongoClient(connection_uri)
        self.coll = self.client.get_database()[self.__COLL__]

    def create(self: Self, url: str) -> str:
        tiny = self.coll.find_one({self.__url: url})
        if tiny is None:
            tiny = {
                self.__slug: self.generate_slug(),
                self.__url: url,
                self.__last_accessed: datetime.utcnow(),
            }
            self.coll.insert_one(tiny)
        return tiny[self.__slug]

    def lookup(self: Self, slug: str) -> str:
        tiny = self.coll.find_one({self.__slug: slug})
        if tiny is None:
            raise Exception(f'Slug "{slug}" in invalid or has expired')

        self.coll.update_one(
            {self.__slug: slug},
            {"$set": {self.__last_accessed: datetime.utcnow()}},
        )
        return tiny["url"]

    def cleanup(self: Self, **kwargs):
        limit = datetime.utcnow() - timedelta(**kwargs)
        query = {self.__last_accessed: {"$lte": limit}}
        if (cnt := self.coll.delete_many(query).deleted_count) > 0:
            self.app.logger.info(f"Removed {cnt} record(s) from database.")

    def teardown(self: Self, exception: Optional[Exception]):
        pass
