"""Main module for this repo"""

from argparse import ArgumentParser
from argparse import Namespace
from os import system
from pandas import Series
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


def save_data(data_info: CleanDataObject):
    """Stores the data on disk as an ARFF and a CSV"""

    csv_name: str = 'data.csv'
    arff_name: str = 'data.arff'

    # Save as CSV
    data_info.data.to_csv(csv_name, index=False)

    # Copy the CSV to make the ARFF
    cp_cmd: str = 'cp {} {}'.format(csv_name, arff_name)
    system(cp_cmd)

    # Open the ARFF as a text file to edit
    with open(arff_name, 'r') as f:
        arff: str = f.read()

    # Remove the first line
    arff: list = arff.split('\n')
    arff: list = arff[1:]

    # Remove empty strings
    while '' in arff:
        arff.remove('')

    # Make the header
    header: list = ['@RELATION ADNI']

    col_names: list = list(data_info.col_types)
    for col_name in col_names:
        line: str = '@ATTRIBUTE {}'.format(col_name)

        is_numeric: bool = data_info.col_types.loc[0, col_name] == 'numeric'

        if is_numeric:
            line += ' ' + 'NUMERIC'
        else:
            col: Series = data_info.data[col_name]
            categories: set = set(col.unique())
            line += ' ' + str(categories).replace(' ', '')

        header.append(line)

    header.append('@DATA')

    # Attach the header to the ARFF
    header.extend(arff)
    arff: list = header

    # Rewrite the ARFF with the header included
    with open(arff_name, 'w') as f:
        for line in arff:
            f.write(line + '\n')


def main(argv: list):
    """
    :param argv: The list of program arguments minus the name of the program that by default comes first
    :return: None
    """

    args: Namespace = parse_args(argv)

    # Process the data
    data: CleanDataObject = clean_data(data_path=args.data_path, data_types_path=args.data_types_path)

    # Save the data on disk in the proper format
    save_data(data_info=data)


if __name__ == MAIN_NAME:
    # Pass in the program arguments minus the name of the program
    main(sys.argv[1:])
