# Quick Start

<!-- TOC start -->
- [Deploy RickRoller](#deploy-rickroller)
  * [Run directly](#run-directly)
  * [Using a Docker container](#using-a-docker-container)
- [Available Environment Variables](#available-environment-variables)
<!-- TOC end -->


<!-- TOC --><a name="deploy-rickroller"></a>
## Deploy RickRoller

RickRoller is a Python application that can run locally or from a Docker container.

<!-- TOC --><a name="run-directly"></a>
### Run directly

This project is coded in Python and uses *poetry*. After cloning the project, run:
```bash
# install dependencies and package (to do once)
poetry install

# launch a basic Flask server (for development only)
poetry run rickroll --debug # use --debug/-d for auto-reload
```


<!-- TOC --><a name="using-a-docker-container"></a>
### Using a Docker container

The Docker image is available for download from GitHub packages (`ghcr.io`) and Docker Hub (`docker.io`).
For example:
```bash
docker run --rm -p 8080:8080 derlin/rickroller:latest
```

If you want to build your own, clone the project and run:
```bash
docker build -t derlin/rickroller:latest .
docker run --rm -p 8080:8080 derlin/rickroller:latest
```

The container exposes port `8080`.
In case you are serving the app under a prefix, pass this environment variable to the docker container:
```bash
SCRIPT_NAME=/your-prefix
```

To increase the number of HTTP workers (see [gunicorn: How Many Workers?](https://docs.gunicorn.org/en/stable/design.html#how-many-workers)),
pass this environment variable:
```bash
WORKERS=3 # default to 2
```

<!-- TOC --><a name="available-environment-variables"></a>
## Available Environment Variables

The application can be tuned using environment variables.

**Security**

* `APP_SECRET_KEY`: The Flask Secret Key used for CSRF tokens and sessions. Default to `urandom(10)`.
* `BEHIND_PROXY`: If set to a truthy value (one of `1`, `t`, `true`, `yes`, `y` case-insensitive),
  the app will trust and honour the `X-Forwarded-*` headers (up to one level). Only use it when the app runs behind
  a reverse proxy. See [ProxyFix](https://werkzeug.palletsprojects.com/en/latest/middleware/proxy_fix/)
  for more information.

**Persistence** 

See [docs/persistence](persistence.md).

* `DATABASE_URL`: enable URL shortening feature. Empty means do not use any database,
* `CLEANUP_INTERVAL` and `CLEANUP_INTERVAL_UNITS`: How often should we clean the database of old entries,
* `SLUG_RETENTION` and `SLUG_RETENTION_UNITS`: How old an entry must be for it to be removed from the database,
* `MAX_URLS_PER_USER`: How many URLs can the same IP create before being blocked.

**Docker**

* `WORKERS`: number of gunicorn workers to spawn (`> 1`).