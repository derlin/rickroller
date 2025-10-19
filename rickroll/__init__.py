import urllib
import secrets
from datetime import timedelta
from os import getenv, urandom

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_apscheduler import APScheduler
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
try:
    from flask_talisman import Talisman
    TALISMAN_AVAILABLE = True
except ImportError:
    TALISMAN_AVAILABLE = False

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
from validators.url import url as urlvalidate
from werkzeug.exceptions import NotFound
from werkzeug.middleware.proxy_fix import ProxyFix

from .db import PersistenceError, init_persistence
from .rickroller import RickRoller, RickRollError


def create_app():
    # == PARSE ENVIRONMENT
    # Generate a cryptographically secure secret key (256 bits)
    env_secret_key = getenv("APP_SECRET_KEY", secrets.token_urlsafe(32))
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
    
    # Security configurations
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year

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

    # Add security headers if Flask-Talisman is available
    if TALISMAN_AVAILABLE:
        # Content Security Policy for this application
        csp = {
            'default-src': "'self'",
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Required for rickroll JavaScript injection
                "www.youtube.com",
                "*.giphy.com"
            ],
            'style-src': [
                "'self'", 
                "'unsafe-inline'",  # Required for CSS styling
                "fonts.googleapis.com"
            ],
            'img-src': [
                "'self'",
                "*",  # Required for rickroll images from external sites
                "data:"
            ],
            'font-src': [
                "'self'",
                "fonts.googleapis.com",
                "fonts.gstatic.com"
            ],
            'connect-src': "'self'",
            'frame-src': [
                "'self'",
                "www.youtube.com",
                "*.giphy.com"
            ],
            'object-src': "'none'",
            'base-uri': "'self'"
        }
        
        Talisman(
            app,
            force_https=not app.debug,  # Only force HTTPS in production
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,  # 1 year
            content_security_policy=csp,
            frame_options='SAMEORIGIN',
            referrer_policy='strict-origin-when-cross-origin'
        )
        app.logger.info("Security headers enabled via Flask-Talisman")
    else:
        app.logger.warning("Flask-Talisman not installed - security headers disabled")

    # Add rate limiting if available
    limiter = None
    if LIMITER_AVAILABLE:
        # Use Redis if available, otherwise in-memory storage
        redis_url = getenv("REDIS_URL", getenv("RATE_LIMIT_STORAGE_URL"))
        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            storage_uri=redis_url,
            default_limits=["100 per hour", "20 per minute"]
        )
        app.logger.info("Rate limiting enabled")
    else:
        app.logger.warning("Flask-Limiter not installed - rate limiting disabled")

    safe_exceptions = [RickRollError, PersistenceError, CSRFError]

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the full exception details for debugging (server-side only)
        app.logger.error(f"Exception at {request.url}", exc_info=(type(e), e, e.__traceback__))
        
        if isinstance(e, NotFound):
            flash('404 - The requested page does not exist.')
        elif any(isinstance(e, cls) for cls in safe_exceptions):
            # Only show safe exception messages to users
            flash(str(e), "error")
        else:
            # Don't reveal internal error details to users in production
            if app.debug:
                flash(f"Debug: {type(e).__name__}: {str(e)}", "error")
            else:
                flash("An unexpected error occurred. Please try again later.", "error")
        
        return redirect(url_for("index"))

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            if (url := request.form.get("url")) is not None:
                # Sanitize and validate URL input
                url = url.strip()
                if len(url) > 2048:  # Reasonable URL length limit
                    raise Exception("URL too long (maximum 2048 characters)")
                
                url = urllib.parse.unquote(url)  # may be url-encoded
                
                # Enhanced URL validation
                if not urlvalidate(url):
                    raise Exception("The provided URL is invalid.")
                
                # Additional security check for URL scheme
                parsed_url = urllib.parse.urlparse(url)
                if parsed_url.scheme not in ['http', 'https']:
                    raise Exception("Only HTTP and HTTPS URLs are allowed.")
                
                slug = persistence.get(url, client_ip())
                redirects_after = 0
                if "redirect_on_scroll" in request.form:
                    try:
                        num_scrolls = request.form.get("num_scrolls", "0")
                        redirects_after = int(num_scrolls)
                        # Validate scroll redirect count
                        if redirects_after < 0 or redirects_after > 99:
                            raise ValueError("Invalid scroll count")
                    except (ValueError, TypeError):
                        raise Exception("Invalid number of scrolls specified.")
                
                return redirect(url_for("rickroll", n=redirects_after, slug=slug))

            raise Exception("Missing URL in form")

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
        """Get the client IP address safely, considering proxy headers only when behind a trusted proxy"""
        if env_behind_proxy:
            # Only trust X-Forwarded-For when explicitly behind a trusted proxy
            if (proxy_data := request.headers.get("X-Forwarded-For", None)) is not None:
                # Get the first IP in the chain (original client)
                ip = proxy_data.split(",")[0].strip()
                # Validate the IP address format
                try:
                    from ipaddress import ip_address
                    ip_address(ip)  # This will raise an exception for invalid IPs
                    return ip
                except ValueError:
                    app.logger.warning(f"Invalid IP in X-Forwarded-For header: {proxy_data}")
                    return request.remote_addr
            # Also check other proxy headers
            return (request.headers.get("X-Real-IP") or 
                   request.environ.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or
                   request.remote_addr)
        else:
            return request.remote_addr  # Direct connection, use remote_addr

    return app
