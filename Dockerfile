# Inspired from https://gabnotes.org/lighten-your-python-image-docker-multi-stage-builds/

## --------------- Builder Image
FROM python:3.11-alpine3.20 AS venv

# ➤➤➤ install poetry
ENV POETRY_VERSION 1.8.0

# The following line is only to be able to install cffi on arm64 (QEMU)
# The build goes fine on my Mac M1, but fails on Github Actions (arm64), due to
# cffi missing a wheel... For now, just install what is needed to build from source.
# TODO: once cffi has been patched upstream, remove the following line !
RUN apk add gcc musl-dev libffi-dev

# Use manual install, which provides more control and better logs
# see https://python-poetry.org/docs/#ci-recommendations
RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION

WORKDIR /app

# ➤➤➤ install dependencies 
# install specific deps from the project (in /app/.venv)
# and gunicorn, used to run flask in production mode
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root && \
    poetry run pip install gunicorn
# if you are not using gunicorn, use 
#   RUN poetry build
# and in the final image use:
#   COPY --from=venv dist/*.whl .
#   RUN pip install *.whl

## --------------- Final Image
# !! use the same python version and base distro as the build image
FROM python:3.11-alpine3.20 as final

# number of gunicorn workers to use
ARG WORKERS=2
ENV WORKERS=${WORKERS}
# the logging config outputs to stdout, so we need unbuffered !
ENV PYTHONUNBUFFERED=TRUE

EXPOSE 8080
WORKDIR /app

# do NOT run as root (checkov CKV_DOCKER_8)
RUN addgroup -S www && adduser -S app -G www
USER app

# make python point to the venv
ENV PATH="/app/.venv/bin:$PATH"

# get all the dependencies installed in builder
# do not forget to change the permission, we are running as a user from now on
COPY --chown=app:www --from=venv /app/.venv .venv

# gunicorn will automatically find modules in $PWD, and all deps are in venv
COPY gunicorn.conf.py gunicorn.conf.py
COPY rickroll rickroll

# do not use curl, as it would have to be installed only for healthcheck...
# we have requests already, so let's use it !
HEALTHCHECK --start-period=5s --interval=1m --timeout=10s CMD python -c 'import requests' \
    'try:' \
    '  exit(0 if requests.get("http://localhost:8080").status_code == 200 else 1)' \
    'except:' \
    '  exit(1)'

CMD gunicorn --workers ${WORKERS} --preload --bind=0.0.0.0:8080 --forwarded-allow-ips="*" 'rickroll:create_app()'
