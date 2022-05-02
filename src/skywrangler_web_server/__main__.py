import argparse
import logging
import pathlib

from . import __version__
from .server import serve

LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--version", action="version", version=__version__)

    parser.add_argument(
        "--port", metavar="<port>", type=int, help="TCP port for server (default: 8080)"
    )

    parser.add_argument(
        "--web-client-path",
        metavar="<directory>",
        type=pathlib.Path,
        help="path to the web client directory",
    )

    parser.add_argument(
        "--log-level",
        choices=LOG_LEVEL_MAP.keys(),
        default="info",
        help="log level (default: %(default)s)",
    )

    args = parser.parse_args()
    logging.basicConfig(level=LOG_LEVEL_MAP[args.log_level])
    serve(args.port, args.web_client_path)


if __name__ == "__main__":
    main()
