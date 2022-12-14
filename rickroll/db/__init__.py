from .persistence import Persistence, NoPersistence


def init_persistence(app, connection_uri, max_urls_per_ip) -> Persistence:
    # connection_uri should follow:
    #   scheme://username:password@host:port/path?query#fragment
    args = [app, max_urls_per_ip, connection_uri]
    if connection_uri:
        if connection_uri.startswith("mongodb"):
            from .mongo import MongoPersistence

            return MongoPersistence(*args)
        else:
            from .orm import DbPersistence

            return DbPersistence(*args)

    return NoPersistence(*args)
