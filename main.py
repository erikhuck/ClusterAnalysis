"""Main module of this repository: Parses the arguments and calls the chosen handler"""

from argparse import ArgumentParser
from argparse import Namespace
import sys

from handler.arff import arff_handler
from handler.csv import csv_handler
from strings import MAIN_NAME
from strings import DATA_PATH_ARG
from strings import DATA_PATH_ARG_HELP
from strings import DATA_TYPES_PATH_ARG
from strings import DATA_TYPES_PATH_ARG_HELP


def parse_args(argv) -> Namespace:
    """Gets the arguments for this repo"""

    parser: ArgumentParser = ArgumentParser()

    # Create a parser for the arff handler and the csv handler
    subparsers = parser.add_subparsers(dest='handler_type', title='handler_type')
    subparsers.required = True

    # Configure the arff handler
    arff_parser: ArgumentParser = subparsers.add_parser('arff')
    arff_parser.add_argument(
        DATA_PATH_ARG, type=str, required=True,
        help=DATA_PATH_ARG_HELP
    )
    arff_parser.add_argument(
        DATA_TYPES_PATH_ARG, type=str, required=True,
        help=DATA_TYPES_PATH_ARG_HELP
    )

    # Configure the csv handler
    csv_parser: ArgumentParser = subparsers.add_parser('csv')
    csv_parser.add_argument(
        '--arff-path', type=str, required=True,
        help='Path to the ARFF file from which to create the csv'
    )
    csv_parser.add_argument(
        '--kept-feats', type=str, required=True,
        help='Path to the text file containing the selected features'
    )

    args: Namespace = parser.parse_args(argv)
    return args


def main(argv: list):
    """Main function of this module"""

    args: Namespace = parse_args(argv)

    if args.handler_type == 'arff':
        # Make the ARFF to be used with WEKA
        arff_handler(data_path=args.data_path, data_types_path=args.data_types_path)
    elif args.handler_type == 'csv':
        # Make the CSV to be used for deep learning
        csv_handler(arff_path=args.arff_path, kept_feats=args.kept_feats)


if __name__ == MAIN_NAME:
    # Pass in the program arguments minus the name of the program
    main(sys.argv[1:])
