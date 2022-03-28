import argparse
from . import app

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=8080, debug=args.debug)