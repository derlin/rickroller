import argparse

from rickroll import app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    app.run(host="0.0.0.0", port=8080, debug=args.debug)


if __name__ == "__main__":
    main()
