"""Main module of this repository: Parses the arguments and calls the chosen handler"""

from argparse import ArgumentParser, Namespace
import sys

from handler.arff import arff_handler
from handler.csv import csv_handler


def configure_parser(parser: ArgumentParser):
    """Does the configuration for both types of parsers"""

    parser.add_argument(
        '--cohort', type=str, required=True,
        help='Whether the cohort is ADNI or ANM; choices: adni, anm'
    )
    parser.add_argument(
        '--target-col', type=str, required=False,
        help='If specified, process the data as if it is supervised using this column as the targets'
    )


def parse_args(argv) -> Namespace:
    """Gets the arguments for this repo"""

    parser: ArgumentParser = ArgumentParser()

    # Create a parser for the arff handler and the csv handler
    subparsers = parser.add_subparsers(dest='handler_type', title='handler_type')
    subparsers.required = True

    # Configure the arff handler
    arff_parser: ArgumentParser = subparsers.add_parser('arff')
    configure_parser(parser=arff_parser)

    # Configure the csv handler
    csv_parser: ArgumentParser = subparsers.add_parser('csv')
    configure_parser(parser=csv_parser)
    csv_parser.add_argument(
        '--kept-feats', type=str, required=False,
        help='Path to the text file containing the selected features'
    )

    args: Namespace = parser.parse_args(argv)
    return args


def main(argv: list):
    """Main function of this module"""

    args: Namespace = parse_args(argv)

    if args.handler_type == 'arff':
        # Make the ARFF to be used with WEKA
        arff_handler(cohort=args.cohort, target_col=args.target_col)
    elif args.handler_type == 'csv':
        # Make the CSV to be used for deep learning
        csv_handler(cohort=args.cohort, target_col=args.target_col, kept_feats=args.kept_feats)


if __name__ == '__main__':
    # Pass in the program arguments minus the name of the program
    main(sys.argv[1:])
