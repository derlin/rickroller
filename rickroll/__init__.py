import urllib
from datetime import timedelta
from os import getenv, urandom

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_apscheduler import APScheduler
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from validators.url import url as urlvalidate
from werkzeug.exceptions import NotFound
from werkzeug.middleware.proxy_fix import ProxyFix

from .db import PersistenceError, init_persistence
from .rickroller import RickRoller, RickRollError


def create_app():
    # == PARSE ENVIRONMENT
    env_secret_key = getenv("APP_SECRET_KEY", urandom(10))
    env_db_url = getenv("DATABASE_URL")
    env_cleanup_interval_value = int(getenv("CLEANUP_INTERVAL", 15))
    env_cleanup_interval_unit = getenv("CLEANUP_INTERVAL_UNITS", "minutes")
    env_slug_retention_value = int(getenv("SLUG_RETENTION", 60))
    env_slug_retention_unit = getenv("SLUG_RETENTION_UNITS", "minutes")
    env_max_urls_per_user = int(getenv("MAX_URLS_PER_USER", 40))
    env_scroll_redirects_after_default = int(getenv("SCROLL_REDIRECT_AFTER_DEFAULT", 2))
    env_behind_proxy = getenv("BEHIND_PROXY", "false").lower() in ["t", "1", "true", "yes", "y"]
    # ==

    app = Flask(__name__, static_folder="assets")
    app.secret_key = env_secret_key

    if env_behind_proxy:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1, x_for=1, x_port=1)
        app.logger.info("BEHIND_PROXY set to true -> ProxyFix turned on.")

    if server_name := getenv("SERVER_NAME"):
        app.config["SERVER_NAME"] = server_name
        app.logger.info(f"Using server name {server_name}")
    else:
        app.logger.warning("❗Running without the SERVER_NAME set may lead to errors in production")

    persistence = init_persistence(app, env_db_url, env_max_urls_per_user)

    scheduler = APScheduler()
    cleanup_interval = {env_cleanup_interval_unit: env_cleanup_interval_value}
    slug_retention = timedelta(**{env_slug_retention_unit: env_slug_retention_value})

    if persistence.supports_cleanup:
        scheduler.api_enabled = True
        scheduler.init_app(app)
        scheduler.start()
        app.logger.info(
            (
                f"Registered cleanup job to run every {cleanup_interval} with retention"
                f" {slug_retention}"
            ),
        )

    CSRFProtect().init_app(app)

    safe_exceptions = [RickRollError, PersistenceError, CSRFError]

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(request.url, exc_info=(type(e), e, e.__traceback__))
        if isinstance(e, NotFound):
            flash(f'404 - "{request.url}" doesn\'t exist on this server.')
        elif any(isinstance(e, cls) for cls in safe_exceptions):
            flash(str(e), "error")
        else:
            flash(
                f"An unexpected error occurred ({type(e).__name__}). Sorry for the inconvenience.",
                "error",
            )
        return redirect(url_for("index"))

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            if (url := request.form["url"]) is not None:
                url = urllib.parse.unquote(url)  # may be url-encoded
                if not urlvalidate(url):
                    raise Exception("the provided URL is invalid.")
                slug = persistence.get(url, client_ip())
                redirects_after = 0
                if "redirect_on_scroll" in request.form:
                    redirects_after = int(request.form["num_scrolls"])
                return redirect(url_for("rickroll", n=redirects_after, slug=slug))

            raise Exception("Missing url in form")

        return render_template("index.html")

    @app.route("/t<int:n>/<slug>")
    def rickroll(n: int, slug: str):
        return RickRoller.rickroll(
            persistence.lookup(slug),
            rickroll_url=url_for("rolled", _external=True),
            scroll_redirects_after=n,
        )

    @app.route("/gotcha")
    def rolled():
        return render_template("rolled.html")

    @scheduler.task("interval", id="del", **cleanup_interval)
    def cleanup():
        app.logger.info("Running cleanup.")
        persistence.cleanup(retention=slug_retention)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        persistence.teardown(exception)

    @app.context_processor
    def pass_global_flags_to_jinja_templates():
        return {
            "cleanup_enabled": persistence.supports_cleanup,
            "retention": f"{env_slug_retention_value} {env_slug_retention_unit}",
            "scroll_redirects_after": env_scroll_redirects_after_default,
        }

    def client_ip():
        if (proxy_data := request.headers.get("X-Forwarded-For", None)) is not None:
            return proxy_data.split(",")[0]  # first address in list is User IP
        else:
            return request.remote_addr  # For local development

    return app
