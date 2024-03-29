from .persistence import NoPersistence, Persistence, PersistenceError  # noqa


def init_persistence(app, connection_uri, max_urls_per_ip) -> Persistence:
    # connection_uri should follow:
    #   scheme://username:password@host:port/path?query#fragment
    args = [app, max_urls_per_ip, connection_uri]
    if connection_uri:
        if connection_uri.startswith("mongodb"):
            from .mongo import MongoPersistence

            return MongoPersistence(*args)
        else:
            from .sql import DbPersistence

            return DbPersistence(*args)

    return NoPersistence(*args)
