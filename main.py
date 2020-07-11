"""Main module of this repository: Parses the arguments and calls the chosen handler"""

from argparse import ArgumentParser, Namespace
import sys

from handler.phenotypes import phenotypes_handler
from handler.combine import combine_handler
from handler.csv import csv_handler
from handler.cluster import cluster_handler
from handler.arff import arff_handler
from handler.feat_select import feat_select_handler


def add_cohort_arg(parser: ArgumentParser):
    """Adds the cohort argument to a parser"""

    parser.add_argument(
        '--cohort', type=str, required=True,
        help='Whether the cohort is ADNI or ANM; choices: adni, anm'
    )


def add_iteration_arg(parser: ArgumentParser):
    """Adds the iteration argument to a parser"""

    parser.add_argument(
        '--iteration', type=int, required=True,
        help='The clustering iteration (i.e. how many clusterings have been made so far)'
    )


def add_dataset_arg(parser: ArgumentParser):
    """Adds the target column argument to a parser"""

    parser.add_argument(
        '--dataset', type=str, required=True,
        help='The data set to clean or cluster'
    )


def add_n_kept_feats_arg(parser: ArgumentParser):
    """Adds the number of kept features argument to the parser"""

    parser.add_argument(
        '--n-kept-feats', type=int, required=False,
        help='The number of features that have been kept. Exclude argument to use all the features'
    )


def add_n_clusters_arg(parser: ArgumentParser):
    """Adds the number of clusters argument to the parser"""

    parser.add_argument(
        '--n-clusters', type=int, required=True,
        help='The number of clusters to use'
    )


def add_clustering_score_arg(parser: ArgumentParser):
    """Adds the clustering score argument to the parser"""

    parser.add_argument(
        '--clustering-score', type=str, required=False,
        help='The clustering score of the previous clustering'
    )


def add_file_path_args(parser: ArgumentParser):
    """Adds the arguments that are used for constructing file paths to data"""

    add_cohort_arg(parser=parser)
    add_iteration_arg(parser=parser)
    add_dataset_arg(parser=parser)
    add_n_kept_feats_arg(parser=parser)
    add_n_clusters_arg(parser=parser)
    add_clustering_score_arg(parser=parser)


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

    # Configure the csv handler
    csv_parser: ArgumentParser = subparsers.add_parser('csv')
    add_file_path_args(parser=csv_parser)

    # Configure the cluster handler
    cluster_parser: ArgumentParser = subparsers.add_parser('cluster')
    add_file_path_args(parser=cluster_parser)

    # Configure the arff handler
    arff_parser: ArgumentParser = subparsers.add_parser('arff')
    add_file_path_args(parser=arff_parser)

    # Configure the feat-select handler
    feat_select_parser: ArgumentParser = subparsers.add_parser('feat-select')
    add_file_path_args(parser=feat_select_parser)

    args: Namespace = parser.parse_args(argv)

    if hasattr(args, 'clustering_score') and args.clustering_score is None:
        args.clustering_score = 'no_score'

    return args


def main(argv: list):
    """Main function of this module"""

    args: Namespace = parse_args(argv)

    if args.handler_type == 'phenotypes':
        # Process the phenotypic data according to its specific needs
        phenotypes_handler(cohort=args.cohort)
    elif args.handler_type == 'combine':
        # Combine the phenotypes, MRI data, and gene expression data into a single data set
        combine_handler(cohort=args.cohort)
    elif args.handler_type == 'csv':
        # Make the CSV to be used for clustering
        csv_handler(
            cohort=args.cohort, iteration=args.iteration, dataset=args.dataset, n_kept_feats=args.n_kept_feats,
            n_clusters=args.n_clusters, clustering_score=args.clustering_score
        )
    elif args.handler_type == 'cluster':
        # Obtain the cluster labels for the ARFF
        cluster_handler(
            cohort=args.cohort, iteration=args.iteration, dataset=args.dataset, n_kept_feats=args.n_kept_feats,
            n_clusters=args.n_clusters, clustering_score=args.clustering_score
        )
    elif args.handler_type == 'arff':
        # Make the ARFF to be used with WEKA
        arff_handler(
            cohort=args.cohort, iteration=args.iteration, dataset=args.dataset, n_kept_feats=args.n_kept_feats,
            n_clusters=args.n_clusters, clustering_score=args.clustering_score
        )
    elif args.handler_type == 'feat-select':
        # Select the features from the ARFF using WEKA
        feat_select_handler(
            cohort=args.cohort, iteration=args.iteration, dataset=args.dataset, n_kept_feats=args.n_kept_feats,
            n_clusters=args.n_clusters, clustering_score=args.clustering_score
        )


if __name__ == '__main__':
    # Pass in the program arguments minus the name of the program
    main(sys.argv[1:])
