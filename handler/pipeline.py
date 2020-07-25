"""Uses all the handlers involved in clustering and feature selection in a pipeline to find the best clustering"""

from os.path import join, isdir
from os import mkdir, popen, listdir
from shutil import rmtree

ITER_DIR: str = 'iter'


def pipeline_handler(
    cohort: str, dataset: str, cluster_method: str, n_clusters: int, n_iterations: int, do_continue: bool
):
    """Main method of this module"""

    data_dir: str = make_data_dirs(cohort=cohort, dataset=dataset, cluster_method=cluster_method, n_clusters=n_clusters)
    first_iter, n_kept_feats = continue_after_last_iter(data_dir=data_dir, do_continue=do_continue)
    n_iterations += first_iter

    for iteration in range(first_iter, n_iterations):
        print('Iteration:', iteration)

        iter_dir: str = join(data_dir, ITER_DIR + str(iteration))

        if isdir(iter_dir):
            rmtree(iter_dir)

        mkdir(iter_dir)

        # Cluster the data and get the cluster label which corresponds to each individual
        command: str = get_command(
            handler='cluster', cohort=cohort, dataset=dataset, cluster_method=cluster_method, n_clusters=n_clusters,
            iteration=iteration, n_kept_feats=n_kept_feats
        )
        clustering_score: str = popen(command).read()
        clustering_score: float = float(clustering_score)

        print('Clustering Score:', clustering_score)

        # Create the ARFF using the features that remain on this iteration and the cluster labels previously computed
        command: str = get_command(
            handler='arff', cohort=cohort, dataset=dataset, cluster_method=cluster_method, n_clusters=n_clusters,
            iteration=iteration, n_kept_feats=n_kept_feats, clustering_score=clustering_score
        )
        popen(command).read()

        # Select the best portion of the features according to the cluster labels and a WEKA algorithm
        # The amount of remaining features will be smaller than the previous iteration
        command: str = get_command(
            handler='feat-select', cohort=cohort, dataset=dataset, cluster_method=cluster_method, n_clusters=n_clusters,
            iteration=iteration, n_kept_feats=n_kept_feats
        )
        n_kept_feats: str = popen(command).read()
        n_kept_feats: int = int(n_kept_feats)
        print('Number Of Features Remaining:', n_kept_feats)


def get_command(
    handler: str, cohort: str, dataset: str, cluster_method: str, n_clusters: int, iteration: int,
    n_kept_feats: int, clustering_score: float = None
) -> str:
    """Constructs the terminal command for a handler"""

    command: str = 'python3 main.py {} --cohort {} --dataset {} --cluster-method {} --n-clusters {} --iteration {}'
    command: str = command.format(handler, cohort, dataset, cluster_method, n_clusters, iteration)

    if iteration == 0:
        assert n_kept_feats is None
    else:
        assert n_kept_feats is not None
        command += ' --n-kept-feats {}'.format(n_kept_feats)

    if handler == 'arff':
        command += ' --clustering-score {}'.format(clustering_score)

    return command


def make_data_dirs(cohort: str, dataset: str, cluster_method: str, n_clusters: int) -> str:
    """Creates the directories which wil contain all the data"""

    data_dir: str = 'clean-data'

    for subdir in (cohort, dataset, cluster_method, 'k=' + str(n_clusters)):
        data_dir: str = join(data_dir, subdir)

        if not isdir(data_dir):
            mkdir(data_dir)

    return data_dir


def continue_after_last_iter(data_dir: str, do_continue: bool) -> int:
    """Gets the iteration and number of kept features from the latest iteration in order to continue to the next"""

    col_types_path_part: str = 'col-types-'
    csv_path_part: str = '.csv'

    if do_continue:
        # Start where we last left off
        iter_dirs: list = listdir(data_dir)
        assert len(iter_dirs) > 0

        for i in range(len(iter_dirs)):
            iter_dir: str = iter_dirs[i]
            iteration: int = int(iter_dir[len(ITER_DIR):])
            iter_dirs[i] = iteration

        iter_dirs: list = sorted(iter_dirs)
        first_iter: int = iter_dirs[-1]

        if first_iter == 0:
            n_kept_feats = None
        else:
            # Get the number of kept features from the column types CSV saved on the previous iteration
            n_kept_feats = None
            iter_dir: str = join(data_dir, ITER_DIR + str(first_iter - 1))

            for path in listdir(iter_dir):
                if col_types_path_part in path:
                    n_kept_feats: str = path[len(col_types_path_part):-len(csv_path_part)]
                    n_kept_feats: int = int(n_kept_feats)
                    break

            assert n_kept_feats is not None

        return first_iter, n_kept_feats
    else:
        # Start from the beginning
        return 0, None
