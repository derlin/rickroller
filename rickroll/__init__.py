from http.client import HTTPException
from flask import Flask, request, render_template, flash
from validators.url import url as urlvalidate
import urllib

from .rickroller import RickRoller

app = Flask(__name__, static_folder="assets")


@app.errorhandler(Exception)
def handle_exception(e):
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
