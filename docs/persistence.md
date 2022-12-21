# Using the URL shortener feature for better rickrolls

By default, RickRoll stores the original URL to rickroll directly
in the URL. For example, when rickrolling https://dev.to, the rickrolled
page is available at:
```url
http://localhost:8080/t/https%253A%252F%252Fdev.to
```

When sharing such URLs, your coworkers or friends may get very suspicious
and never actually click on the link.

To avoid such suspicion, the idea is to make the service behave like an URL
shortener, so the rickrolled URL would look like:
```url
http://localhost:8080/t/52f5bD768bCCAbe
```

The part after the `/t/` is called the *slug*.

This shortener feature, however, requires a kind of persistence.
Supported databases are:

* SQLite
* PostgreSQL
* MongoDB

------

<!-- TOC start -->
- [Enabling URL shortening](#enabling-url-shortening)
  * [Using an in-memory database](#using-an-in-memory-database)
  * [Using an SQLite database](#using-an-sqlite-database)
  * [Using a PostgreSQL database](#using-a-postgresql-database)
  * [Using a MongoDB database](#using-a-mongodb-database)
- [Configuration options](#configuration-options)
  * [Database cleanup](#database-cleanup)
  * [Max URL per user](#max-url-per-user)
<!-- TOC end -->

-----

<!-- TOC --><a name="enabling-url-shortening"></a>
## Enabling URL shortening

To enable the URL shortening feature, all you need is a database,
and to instruct rickroller to use it by setting the environment
variable `DATABASE_URL`:
```bash
export DATABASE_URL=scheme://username:password@host:port/path?query#fragment
```

Supported schemes are: `postgresql`, `sqlite`, `mongo`, `mongo+srv`.

<!-- TOC --><a name="using-an-in-memory-database"></a>
### Using an in-memory database

For **local development only**, it is possible to use an in-memory SQLite database,
by setting:
```bash
DATABASE_URL=sqlite://
```

Note that this won't work from within a Docker container, as gunicorn uses multiple
workers in different processes!

<!-- TOC --><a name="using-an-sqlite-database"></a>
### Using an SQLite database

SQLite databases are stored inside files. To use a file in the local directory:
```bash
# notice the triple slash for relative path!
DATABASE_URL=sqlite:///rickroll.db poetry run python -m rickroll
```

When running in Docker, you need to mount a volume first, then use four slashes (`sqlite:////`)
to pass an absolute path to sqlite. For example:
```bash
# Use the file /tmp/rickroll.db, mounted as /db/rickroll.db inside the container
docker run \
    -p 8080:8080 \
    -v /tmp:/db \
    -e DATABASE_URL=sqlite:////db/rickroll.db \
    derlin/rickroller:latest
```

<!-- TOC --><a name="using-a-postgresql-database"></a>
### Using a PostgreSQL database

To get a PostgreSQL database running locally, you can use the following `docker-compose.yaml`:
```yaml
services:
  postgres:
    image: postgres
    ports:
      - 5432:5432
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: rickroll
      PGDATA: /var/lib/postgresql/data/pgdata
    # Uncomment the following lines to persist the data
    #volumes:
    #  - ./data/db:/var/lib/postgresql/data
```

Once running (using `docker compose up -d`), you can start RickRoller using:
```bash
DATABASE_URL=postgresql://user:password@localhost/rickroll poetry run python -m rickroll
```

<!-- TOC --><a name="using-a-mongodb-database"></a>
### Using a MongoDB database

To get a MongoDB database running locally, you can use the following `docker-compose.yaml`:
```yaml
services:
  mongo:
    image: mongo
    restart: always
    ports:
      - 27017:27017
    environment:
      MONGO_INITDB_ROOT_USERNAME: user
      MONGO_INITDB_ROOT_PASSWORD: password
      MONGO_INITDB_DATABASE: rickroll

# mongodb://root:example@localhost:27017/urls?authSource=admin
# mongodb+srv://derrollin-Wfg45cZU39:Zh_ke7fvjFNv-G7Q74q9-ReWM4P-z_GV5svKq-h6u_LG3Nc5yWdtJ@cluster0.noly4wt.mongodb.net/rickroll?retryWrites=true&w=majority
```

Once running (using `docker compose up -d`), you can start RickRoller using:
```bash
DATABASE_URL=mongodb://user:password@localhost:27017/rickroll?authSource=admin poetry run python -m rickroll
```

You can also use a **free Mongo instance** on e.g. https://mongodb.com (Mongo ATLAS).
In this case, ensure you create a database user with a strong password and add the IP `0.0.0.0/0` to the access list.
You can then click on the "connect" button in the main view, choose "connect your application" and copy the
connection string starting with `mongodb+srv`. For example:
```bash
DATABASE_URL=mongodb+srv://super-secret-user:<password>@cluster0.some-subdomain.mongodb.net/?retryWrites=true&w=majority
```

<!-- TOC --><a name="configuration-options"></a>
## Configuration options

<!-- TOC --><a name="database-cleanup"></a>
### Database cleanup

Without any proper handling, the database could grow indefinitely.

RickRoller comes by default with a cleanup policy: that ensures any idle slug
is discarded after a while.

More precisely, the application runs a cron job every `X units`, that discards any
entry in the database that hasn't been used in the last `Y units`.

`X` and `Y` are integers, and `units` should be one of `hours`, `minutes` or `seconds`.
Those are configurable with environment variables. Here are the defaults:
```bash
# X => interval at which to run the cleanup job
CLEANUP_INTERVAL=15
CLEANUP_INTERVAL_UNITS="minutes"
# Y => a slug should have been accessed in the given
# interval to be kept in the database (default: the last hour)
SLUG_RETENTION=60
SLUG_RETENTION_UNITS="minutes"
```

<!-- TOC --><a name="max-url-per-user"></a>
### Max URL per user

To avoid people flooding the service, RickRoll sets a limit on the number of slugs
created by the same user. Since there is no login required, here "user" means
IP address.

RickRoll sets the limit to 40 by default, but you can change it using the following
environment variable:
```bash
MAX_URLS_PER_USER=40
```