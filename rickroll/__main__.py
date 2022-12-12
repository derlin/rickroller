import argparse
from rickroll import app
from rickroll.log import logging_config
from logging.config import dictConfig

if __name__ == "__main__":
    # apply logging config manually when not running with gunicorn
    dictConfig(logging_config("DEBUG"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="8080")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
