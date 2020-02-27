"""Main module for this repo"""

from argparse import ArgumentParser
from argparse import Namespace
import sys

from clean_data import clean_data, CleanDataObject
from strings import MAIN_NAME
from strings import DATA_PATH_ARG
from strings import DATA_PATH_ARG_HELP
from strings import DATA_TYPES_PATH_ARG
from strings import DATA_TYPES_PATH_ARG_HELP


def parse_args(argv) -> Namespace:
    """Gets the arguments for this repo"""

    parser: ArgumentParser = ArgumentParser()

    parser.add_argument(
        DATA_PATH_ARG, type=str, required=True,
        help=DATA_PATH_ARG_HELP
    )
    parser.add_argument(
        DATA_TYPES_PATH_ARG, type=str, required=True,
        help=DATA_TYPES_PATH_ARG_HELP
    )

    args: Namespace = parser.parse_args(argv)
    return args


def save_data(data: CleanDataObject):
    """Stores the data on disk as an ARFF and a CSV"""
    pass


def main(argv: list):
    """
    :param argv: The list of program arguments minus the name of the program that by default comes first
    :return: None
    """

    args: Namespace = parse_args(argv)

    # Process the data
    data: CleanDataObject = clean_data(data_path=args.data_path, data_types_path=args.data_types_path)

    # Save the data on disk in the proper format
    save_data(data=data)


if __name__ == MAIN_NAME:
    # Pass in the program arguments minus the name of the program
    main(sys.argv[1:])
