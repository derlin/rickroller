# This logging configuration should be applied in gunicorn (see gunicorn.conf.py)
# and when running flask directly (see __main__.py).
# NOTES:
#  - this requires PYTHONUNBUFFERED=True as we stream to stdout
#  - since the app is created in __init__.py (which runs before anything else),
#    the default handlers need to be cleared to avoid duplicate logs (app.logger.handlers.clear())


def logging_config(app_log_level):
    return {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {"format": "%(asctime)s %(levelname)8s | %(message)s"},
            "app": {
                "format": "%(asctime)s %(levelname)8s > %(message)s  (%(filename)s:%(lineno)s)",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "console_app": {
                "class": "logging.StreamHandler",
                "formatter": "app",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "gunicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "gunicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "rickroll": {
                "handlers": ["console_app"],
                "level": app_log_level,
                "propagate": False,
            },
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
