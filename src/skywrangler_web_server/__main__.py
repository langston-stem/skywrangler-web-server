import argparse
import logging
import pathlib

from .server import serve

LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--web-client-path",
        metavar="<directory>",
        type=pathlib.Path,
        help="path to the web client directory",
    )

    parser.add_argument(
        "--log-level",
        choices=LOG_LEVEL_MAP.keys(),
        default="warning",
        help="log level (default: %(default)s)",
    )

    args = parser.parse_args()
    logging.basicConfig(level=LOG_LEVEL_MAP[args.log_level])
    serve(args.web_client_path)


if __name__ == "__main__":
    main()
