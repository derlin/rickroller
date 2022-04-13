# Inspired from https://gabnotes.org/lighten-your-python-image-docker-multi-stage-builds/

## --------------- Builder Image
FROM python:3.9-alpine3.15 AS venv

# ➤➤➤ install poetry
#ENV POETRY_VERSION=1.1.4
RUN apk add curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH /root/.poetry/bin:$PATH

WORKDIR /app

# ➤➤➤ setup venv
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# ➤➤➤ install dependencies in venv
# used to run flask on prod image
RUN pip install gunicorn
# install specific deps from the project
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-root
# if you are not using gunicorn, use 
#   RUN poetry build
# and in the final image use:
#   COPY --from=venv dist/*.whl .
#   RUN pip install *.whl

## --------------- Final Image
# !! use the same python version and base distro as the build image
FROM python:3.9-alpine3.15 as final

# number of gunicorn workers to use
ARG WORKERS=1
ENV WORKERS=${WORKERS}

EXPOSE 8080
WORKDIR /app

# do NOT run as root (checkov CKV_DOCKER_8)
RUN addgroup -S www && adduser -S app -G www
USER app

# make python point to the venv
ENV PATH="/app/venv/bin:$PATH"

# get all the dependencies installed in builder
COPY --from=venv /app/venv venv

# gunicorn will automatically find modules in $PWD, and all deps are in venv
COPY rickroll rickroll

# do not use curl, as it would have to be installed only for healthcheck...
# we have requests already, so let's use it !
HEALTHCHECK --start-period=5s --interval=1m --timeout=10s CMD python -c 'import requests' \
    'try:' \
    '  exit(0 if requests.get("http://localhost:8080").status_code == 200 else 1)' \
    'except:' \
    '  exit(1)'

ENTRYPOINT ["sh", "-c", "gunicorn --workers ${WORKERS} --preload --bind :8080 rickroll:app"]