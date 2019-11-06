from argparse import ArgumentParser
from argparse import Namespace
import sys

from strings import MAIN_NAME
from strings import DATA_PATH_ARG
from strings import DATA_PATH_ARG_HELP


def parse_args(argv) -> Namespace:
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument(
        DATA_PATH_ARG, type=str, required=True,
        help=DATA_PATH_ARG_HELP
    )

    args: Namespace = parser.parse_args(argv)
    return args


def main(argv: list):
    """
    :param argv: The list of program arguments minus the name of the program that by default comes first
    :return: None
    """

    args: Namespace = parse_args(argv)
    pass


if __name__ == MAIN_NAME:
    # Pass in the program arguments minus the name of the program
    main(sys.argv[1:])
