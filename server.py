from flask import Flask, request, render_template
from validators.url import url as urlvalidate
from rickroller import RickRoller
import urllib

app = Flask(__name__, static_folder='assets')

@app.route('/')
def rickroll():
    if (url := request.args.get('u')) is not None:
        url = urllib.parse.unquote(url) # may be url-encoded
        if not urlvalidate(url):
            return f'Invalid URL {url}'

        return RickRoller.rickroll(url)

    return render_template('index.html')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=8080, debug=args.debug)