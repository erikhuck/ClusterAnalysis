"""Uses all the handlers involved in clustering and feature selection in a pipeline to find the best clustering"""

from os.path import join, isdir
from os import mkdir, popen
from shutil import rmtree


def pipeline_handler(cohort: str, dataset: str, n_clusters: int, n_iterations: int):
    """Main method of this module"""

    n_kept_feats = None

    for iteration in range(n_iterations):
        print('Iteration:', iteration)

        # Create the directory that will store the data for this iteration
        iter_dir: str = join('clean-data', cohort, dataset, 'iter' + str(iteration))

        if isdir(iter_dir):
            rmtree(iter_dir)

        mkdir(iter_dir)

        # Cluster the data and get the cluster label which corresponds to each individual
        command: str = get_command(
            handler='cluster', cohort=cohort, iteration=iteration, dataset=dataset, n_kept_feats=n_kept_feats,
            n_clusters=n_clusters
        )
        clustering_score: str = popen(command).read()
        clustering_score: float = float(clustering_score)

        print('Clustering Score:', clustering_score)

        # Create the ARFF using the features that remain on this iteration and the cluster labels previously computed
        command: str = get_command(
            handler='arff', cohort=cohort, iteration=iteration, dataset=dataset, n_kept_feats=n_kept_feats,
            n_clusters=n_clusters, clustering_score=clustering_score
        )
        popen(command).read()

        # Select the best portion of the features according to the cluster labels and a WEKA algorithm
        # The amount of remaining features will be smaller than the previous iteration
        command: str = get_command(
            handler='feat-select', cohort=cohort, iteration=iteration, dataset=dataset, n_kept_feats=n_kept_feats,
            n_clusters=n_clusters
        )
        n_kept_feats: str = popen(command).read()
        n_kept_feats: int = int(n_kept_feats)
        print('Number Of Features Remaining:', n_kept_feats)


def get_command(
    handler: str, cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int,
    clustering_score: float = None
) -> str:
    """Constructs the terminal command for a handler"""

    command: str = 'python3 main.py {} --cohort {} --iteration {} --dataset {}'.format(
        handler, cohort, iteration, dataset
    )

    if iteration == 0:
        assert n_kept_feats is None
    else:
        assert n_kept_feats is not None
        command += ' --n-kept-feats {}'.format(n_kept_feats)

    command += ' --n-clusters {}'.format(n_clusters)

    if handler == 'arff':
        command += ' --clustering-score {}'.format(clustering_score)

    return command
