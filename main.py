"""Main module of this repository: Parses the arguments and calls the chosen handler"""

from argparse import ArgumentParser, Namespace
import sys

from handler.phenotypes import phenotypes_handler
from handler.combine import combine_handler
from handler.arff import arff_handler
from handler.csv import csv_handler
from handler.cluster import cluster_handler


def add_cohort_arg(parser: ArgumentParser):
    """Adds the cohort argument to a parser"""

    parser.add_argument(
        '--cohort', type=str, required=True,
        help='Whether the cohort is ADNI or ANM; choices: adni, anm'
    )


def add_target_col_arg(parser: ArgumentParser):
    """Adds the target column argument to a parser"""

    parser.add_argument(
        '--target-col', type=str, required=False,
        help='If specified, process the data as if it is supervised using this column as the targets'
    )


def parse_args(argv) -> Namespace:
    """Gets the arguments for this repo"""

    parser: ArgumentParser = ArgumentParser()

    subparsers = parser.add_subparsers(dest='handler_type', title='handler_type')
    subparsers.required = True

    # Configure the phenotypes handler
    phenotypes_parser: ArgumentParser = subparsers.add_parser('phenotypes')
    add_cohort_arg(parser=phenotypes_parser)

    # Configure the combine handler
    combine_parser: ArgumentParser = subparsers.add_parser('combine')
    add_cohort_arg(parser=combine_parser)

    # Configure the arff handler
    arff_parser: ArgumentParser = subparsers.add_parser('arff')
    add_cohort_arg(parser=arff_parser)

    # Configure the csv handler
    csv_parser: ArgumentParser = subparsers.add_parser('csv')
    add_cohort_arg(parser=csv_parser)
    csv_parser.add_argument(
        '--kept-feats', type=str, required=False,
        help='Path to the text file containing the selected features'
    )

    # Configure the cluster handler
    cluster_parser: ArgumentParser = subparsers.add_parser('cluster')
    add_cohort_arg(parser=cluster_parser)
    cluster_parser.add_argument(
        '--n-clusters', type=int, required=False,
        help='The number of clusters to use'
    )

    args: Namespace = parser.parse_args(argv)
    return args


def main(argv: list):
    """Main function of this module"""

    args: Namespace = parse_args(argv)

    if args.handler_type == 'phenotypes':
        phenotypes_handler(cohort=args.cohort)
    elif args.handler_type == 'combine':
        combine_handler(cohort=args.cohort)
    elif args.handler_type == 'arff':
        # Make the ARFF to be used with WEKA
        arff_handler(cohort=args.cohort)
    elif args.handler_type == 'csv':
        # Make the CSV to be used for deep learning
        csv_handler(cohort=args.cohort, kept_feats=args.kept_feats)
    elif args.handler_type == 'cluster':
        cluster_handler(n_clusters=args.n_clusters, cohort=args.cohort)


if __name__ == '__main__':
    # Pass in the program arguments minus the name of the program
    main(sys.argv[1:])
