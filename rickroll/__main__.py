import argparse
from logging.config import dictConfig

from rickroll import create_app
from rickroll.log import logging_config


def main():
    # apply logging config manually when not running with gunicorn
    # this must be done *before* creating the app !
    dictConfig(logging_config("DEBUG"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="8080")
    parser.add_argument("--host", default="0.0.0.0")  # noqa
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    create_app().run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
