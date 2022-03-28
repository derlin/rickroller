from flask import Flask, request, render_template
from validators.url import url as urlvalidate
import urllib

from .rickroller import RickRoller

app = Flask(__name__, static_folder='assets')

@app.route('/')
def rickroll():
    if (url := request.args.get('u')) is not None:
        url = urllib.parse.unquote(url) # may be url-encoded
        if not urlvalidate(url):
            return f'Invalid URL {url}'

        return RickRoller.rickroll(url)

    return render_template('index.html')