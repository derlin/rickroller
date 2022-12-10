from datetime import datetime, timedelta
from typing import Self, Optional

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

from .persistence import Persistence

_SQLITE_IN_MEMORY = "sqlite://"

Base = declarative_base()


class TinyUrl(Base):
    __tablename__ = "urls"

    slug = Column(String(), primary_key=True)
    url = Column(String(), unique=True)
    last_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<tinyurl={self.slug} => {self.url} ({self.last_time})>"


class DbPersistence(Persistence):
    supports_cleanup = True

    def __init__(self: Self, app, connection_uri):
        self.app = app
        engine = self.__create_engine(connection_uri)
        self.db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
        Base.query = self.db_session.query_property()
        Base.metadata.create_all(bind=engine)

    def create(self: Self, url: str) -> str:
        tiny = self.db_session.query(TinyUrl).filter(TinyUrl.url == url).first()
        if tiny is None:
            tiny = TinyUrl(url=url, slug=self.generate_slug())
            self.db_session.add(tiny)
            self.db_session.commit()
        return tiny.slug

    def lookup(self: Self, slug: str) -> str:
        tiny = self.db_session.query(TinyUrl).filter(TinyUrl.slug == slug).first()
        if tiny is None:
            raise Exception(f'Slug "{slug}" in invalid or has expired')
        return tiny.url

    def cleanup(self: Self, **kwargs):
        limit = datetime.utcnow() - timedelta(**kwargs)
        query = self.db_session.query(TinyUrl).filter(TinyUrl.last_time < limit)
        if (cnt := query.count()) > 0:
            self.app.logger.info(f"Removing {cnt} record(s) from database.")
            query.delete()

    def teardown(self: Self, exception: Optional[Exception]):
        if exception is not None:
            self.db_session.rollback()
        else:
            self.db_session.commit()
        self.db_session.remove()

    @classmethod
    def __create_engine(cls: Self, connection_uri) -> Engine:
        from sqlalchemy import create_engine as sqlalchemy_create_engine

        if connection_uri == _SQLITE_IN_MEMORY:
            from sqlalchemy.pool import StaticPool

            return sqlalchemy_create_engine(
                "sqlite://",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )

        return sqlalchemy_create_engine(connection_uri)
