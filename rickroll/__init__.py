from os import getenv, urandom
import urllib
from datetime import timedelta

from http.client import HTTPException
from flask import Flask, request, render_template, redirect, url_for, flash
from validators.url import url as urlvalidate

from flask import Flask, request, render_template
from flask_wtf import CSRFProtect
from flask_apscheduler import APScheduler

from .db import init_persistence
from .rickroller import RickRoller


def create_app():

    # == PARSE ENVIRONMENT
    env_secret_key = getenv("APP_SECRET_KEY", urandom(10))
    env_db_url = getenv("DATABASE_URL")
    env_cleanup_interval_value = int(getenv("CLEANUP_INTERVAL", 15))
    env_cleanup_interval_unit = getenv("CLEANUP_INTERVAL_UNITS", "minutes")
    env_slug_retention_value = int(getenv("SLUG_RETENTION", 60))
    env_slug_retention_unit = getenv("SLUG_RETENTION_UNITS", "minutes")
    env_max_urls_per_user = int(getenv("MAX_URLS_PER_USER", 40))
    # ==

    app = Flask(__name__, static_folder="assets")
    app.secret_key = env_secret_key

    persistence = init_persistence(app, env_db_url, env_max_urls_per_user)

    scheduler = APScheduler()
    cleanup_interval = {env_cleanup_interval_unit: env_cleanup_interval_value}
    slug_retention = timedelta(**{env_slug_retention_unit: env_slug_retention_value})

    if persistence.supports_cleanup:
        scheduler.api_enabled = True
        scheduler.init_app(app)
        scheduler.start()
        app.logger.info(
            f"Registered cleanup job to run every {cleanup_interval} with retention {slug_retention}"
        )

    CSRFProtect().init_app(app)

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(request.url, exc_info=(type(e), e, e.__traceback__))
        if isinstance(e, HTTPException):
            return e  # pass through HTTP errors

        flash(str(e), "error")
        return redirect(url_for("index"))

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            if (url := request.form["url"]) is not None:
                url = urllib.parse.unquote(url)  # may be url-encoded
                if not urlvalidate(url):
                    raise Exception(f"the provided URL is invalid.")
                slug = persistence.get(url, client_ip())
                return redirect(url_for("rickroll", slug=slug))

            raise Exception("Missing url in form")

        return render_template("index.html")

    @app.route("/t/<slug>")
    def rickroll(slug: str):
        return RickRoller.rickroll(persistence.lookup(slug))

    @scheduler.task("interval", id="del", **cleanup_interval)
    def cleanup():
        app.logger.info(f"Running cleanup.")
        persistence.cleanup(retention=slug_retention)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        persistence.teardown(exception)

    def client_ip():
        if (proxy_data := request.headers.get("X-Forwarded-For", None)) is not None:
            return proxy_data.split(",")[0]  # first address in list is User IP
        else:
            return request.remote_addr  # For local development

    return app
