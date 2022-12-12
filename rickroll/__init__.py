import urllib
from http.client import HTTPException
from validators.url import url as urlvalidate

from flask import Flask, request, render_template

from .rickroller import RickRoller

app = Flask(__name__, static_folder="assets")
# If we do not clear the default handlers, we will have duplicate logs
# This is because we are in __init__.py, so neither main nor gunicorn
# have run yet (they will set the logging config later)
app.logger.handlers.clear()


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(request.url, exc_info=(type(e), e, e.__traceback__))
    if isinstance(e, HTTPException):
        return e  # pass through HTTP errors
    return render_template("index.html", ex=e, url=request.args.get("u"))


@app.route("/")
def rickroll():
    if (url := request.args.get("u")) is not None:
        url = urllib.parse.unquote(url)  # may be url-encoded
        if not urlvalidate(url):
            raise Exception(f"the provided URL is invalid.")

        return RickRoller.rickroll(url)

    return render_template("index.html")
