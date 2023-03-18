import pytest

from mongomock import MongoClient

from rickroll.db import Persistence, NoPersistence, PersistenceError
from rickroll.db.mongo import MongoPersistence
from rickroll.db.sql import DbPersistence, _SQLITE_IN_MEMORY
from datetime import datetime, timedelta
import contextlib


max_urls_per_user = 3
some_client_ip = "160.98.70.10"


@pytest.fixture
def mongo(monkeypatch, app):
    def mock_collection(*args, **kwargs):
        return MongoClient().db.collection

    monkeypatch.setattr(MongoPersistence, "_get_mongo_collection", mock_collection)
    return MongoPersistence(app, max_urls_per_user, "<connection uri>")


@pytest.fixture
def sql(app):
    return DbPersistence(app, max_urls_per_user, _SQLITE_IN_MEMORY)


@contextlib.contextmanager
def session(db: Persistence, ex: Exception = None):
    try:
        yield db
    finally:
        db.teardown(ex)


@contextlib.contextmanager
def reverse_time(db: Persistence, td: timedelta):
    with pytest.MonkeyPatch.context() as mk:
        original_now = db.now
        mk.setattr(db, "now", lambda: datetime.utcnow() - td)
        yield
        mk.setattr(db, "now", original_now)


def test_no_persistence(app):
    db = NoPersistence(app, max_urls_per_user)

    slug = db.get("https://derlin.ch", some_client_ip)
    assert db.get(db.lookup(slug), "150.9.8.8") == slug

    # check we do not have an exception
    assert db.cleanup(timedelta()) is None
    assert db.teardown(None) is None


@pytest.mark.parametrize("db_fixture", ["mongo", "sql"])
class TestPersistenceImplementations:
    def test_get(self, request, db_fixture):
        db: Persistence = request.getfixturevalue(db_fixture)

        url = "https://example.com"
        slugs = [db.get(url, some_client_ip) for i in range(0, 5)]
        assert len(set(slugs)) == 1
        assert len(slugs[0]) == 15
        assert db.lookup(slugs[0]) == url

        url2 = f"{url}/home"
        slug2 = db.get(url2, some_client_ip)
        assert slugs[0] != slug2
        assert db.lookup(slug2) == url2

        with pytest.raises(PersistenceError, match=".* is invalid or has expired$"):
            db.lookup("unknown-slug")

    def test_max_client_urls(self, request, db_fixture):
        db: Persistence = request.getfixturevalue(db_fixture)

        slugs = [
            db.get(f"https://example.com/{i}", some_client_ip)
            for i in range(0, max_urls_per_user)
        ]
        assert len(set(slugs)) == 3

        assert db.get("https://another-client.com", "127.0.0.1") is not None

        with pytest.raises(PersistenceError, match="Too many urls created.*"):
            db.get("https://one-too-many.com", some_client_ip)

    def test_cleanup(self, request, db_fixture):
        db: Persistence = request.getfixturevalue(db_fixture)

        with session(db):
            with reverse_time(db, timedelta(minutes=10)):
                slug_10minutes = db.get("https://10-minutes.com", some_client_ip)
            with reverse_time(db, timedelta(hours=1)):
                slug_1hour = db.get("https://1-hour.com", some_client_ip)

        with session(db):
            assert db._lookup(slug_10minutes) is not None
            assert db._lookup(slug_1hour) is not None

        with session(db):
            db.cleanup(timedelta(hours=3))
            assert db._lookup(slug_10minutes) is not None
            assert db._lookup(slug_1hour) is not None

        with session(db):
            db.cleanup(timedelta(minutes=30))
            assert db._lookup(slug_10minutes) is not None
            assert db._lookup(slug_1hour) is None

        with session(db):
            db.cleanup(timedelta(minutes=3))
            assert db._lookup(slug_10minutes) is None
            assert db._lookup(slug_1hour) is None

    def test_update_timestamp(self, request, db_fixture):
        db: Persistence = request.getfixturevalue(db_fixture)

        with session(db):
            with reverse_time(db, timedelta(hours=1)):
                slug_1hourA = db.get("https://1-hour-a.com", some_client_ip)
                slug_1hourB = db.get("https://1-hour-b.com", some_client_ip)

        with session(db):
            db.lookup(slug_1hourB)

        with session(db):
            db.cleanup(timedelta(minutes=3))
            assert db._lookup(slug_1hourA) is None
            assert db._lookup(slug_1hourB) is not None
