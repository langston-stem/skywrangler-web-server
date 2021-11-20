import argparse
import logging
import pathlib

from .main import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--web-client-path",
        metavar="<directory>",
        type=pathlib.Path,
        help="path to the web client directory",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    main(args.web_client_path)
