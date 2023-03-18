from datetime import timedelta
from typing import Self

from sqlalchemy import Column, DateTime, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .persistence import Persistence

_SQLITE_IN_MEMORY = "sqlite://"

Base = declarative_base()


class TinyUrl(Base):
    __tablename__ = "urls"

    slug = Column(String(), primary_key=True, nullable=False)
    url = Column(String(), unique=True, nullable=False)
    client_ip = Column(String(), nullable=False)
    last_time = Column(DateTime(), nullable=False)

    def __repr__(self):
        return f"<tinyurl={self.slug} => {self.url} ({self.last_time})>"


class DbPersistence(Persistence):
    supports_cleanup = True

    def __init__(self: Self, app, max_urls_per_ip, connection_uri):
        super().__init__(app, max_urls_per_ip)
        engine = self.__create_engine(connection_uri)
        self.db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine),
        )
        Base.query = self.db_session.query_property()
        Base.metadata.create_all(bind=engine)
        self.app.logger.info("Initialized a SQL database.")

    def _get(self: Self, url: str) -> str | None:
        tiny = self.db_session.query(TinyUrl).filter(TinyUrl.url == url).first()
        return tiny.slug if tiny else None

    def _create(self: Self, url: str, client_ip: str) -> str:
        tiny = TinyUrl(
            url=url,
            slug=self.generate_slug(),
            client_ip=client_ip,
            last_time=self.now(),
        )
        self.__persist(tiny)
        self.app.logger.debug(f"Inserted {tiny} in SQL database.")
        return tiny.slug

    def _lookup(self: Self, slug: str) -> str | None:
        if (tiny := self.db_session.query(TinyUrl).get(slug)) is not None:
            return tiny.url
        return None

    def _update_time_accessed(self: Self, slug: str):
        tiny: TinyUrl = self.db_session.query(TinyUrl).get(slug)
        tiny.last_time = self.now()
        self.__persist(tiny)

    def urls_per_ip(self: Self, ip: str) -> int:
        return self.db_session.query(TinyUrl).filter(TinyUrl.client_ip == ip).count()

    def cleanup(self: Self, retention: timedelta):
        limit = self.now() - retention
        query = self.db_session.query(TinyUrl).filter(TinyUrl.last_time < limit)
        if (cnt := query.count()) > 0:
            self.app.logger.info(f"Removing {cnt} record(s) from database.")
            query.delete()

    def teardown(self: Self, exception: Exception | None):
        self.db_session.remove()

    def __persist(self, tiny: TinyUrl):
        self.db_session.add(tiny)
        self.db_session.commit()

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

        # Avoid "Can't load plugin: sqlalchemy.dialects:postgres"
        # see https://stackoverflow.com/a/72904869/2667536
        if connection_uri.startswith("postgres://"):
            connection_uri = connection_uri.replace("postgres://", "postgresql://", 1)

        return sqlalchemy_create_engine(connection_uri, pool_pre_ping=True)
