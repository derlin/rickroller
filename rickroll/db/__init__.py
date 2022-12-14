from .persistence import Persistence, NoPersistence


def init_persistence(app, connection_uri) -> Persistence:
    # scheme://username:password@host:port/path?query#fragment
    if connection_uri.startswith("mongodb"):
        from .mongo import MongoPersistence

        return MongoPersistence(app, connection_uri)

    if connection_uri:
        from .orm import DbPersistence

        return DbPersistence(app, connection_uri)

    return NoPersistence()
