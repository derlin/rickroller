from rickroll.log import logging_config
from os import getenv

# Apply custom log configuration when using gunicorn
# Note that if this is done from the app itself, it won't be
# applied to all workers...

logconfig_dict = logging_config(getenv("APP_LOGGING_LEVEL", "INFO").upper())
