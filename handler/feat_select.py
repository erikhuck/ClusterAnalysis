"""Selects features from an ARFF using a WEKA feature selection algorithm"""

from os import popen
from pandas import DataFrame, read_csv

from handler.utils import ARFF_PATH, get_data_path, get_col_types_path


def feat_select_handler(cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int):
    """Main method of this module"""

    # We need to get the previous data paths now because n_kept_feats will change after selecting features
    prev_data_path: str = get_data_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    prev_col_types_path: str = get_col_types_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )

    # Load the column types in case n_kept_feats has not been set yet
    # We'll load the rest of the data later
    col_types: DataFrame = read_csv(prev_col_types_path)

    if n_kept_feats is None:
        n_kept_feats: int = col_types.shape[-1]

    # Run the feature selection WEKA algorithm on the ARFF
    arff_path: str = ARFF_PATH.format(cohort, dataset, iteration, n_kept_feats, n_clusters)
    n_kept_feats: int = int(n_kept_feats * 0.9)
    command: str = 'java -cp ~/weka-3-8-4/weka.jar weka.attributeSelection.InfoGainAttributeEval -s '
    command += '"weka.attributeSelection.Ranker -T 0.0 -N {}" -i {}'.format(n_kept_feats, arff_path)
    rank_output: str = popen(command).read()

    # Create a list of the features that were kept / selected
    rank_output: list = rank_output.split('\n')
    cut_idx: int = rank_output.index('Ranked attributes:') + 1
    rank_output: list = rank_output[cut_idx:]

    while '' in rank_output:
        rank_output.remove('')

    feats_to_keep: list = []

    for line in rank_output:
        if 'Selected attributes:' in line:
            break

        line = line.split(' ')
        feat: str = line[-1]
        feats_to_keep.append(feat)

    assert n_kept_feats == len(feats_to_keep)
    print(n_kept_feats)

    # Now load the rest of the data in addition to the column types
    data: DataFrame = read_csv(prev_data_path)

    # Select the features from the previous data
    data: DataFrame = data[feats_to_keep].copy()
    col_types: DataFrame = col_types[feats_to_keep].copy()
    next_data_path: str = get_data_path(
        cohort=cohort, dataset=dataset, iteration=iteration + 1, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    next_col_types_path: str = get_col_types_path(
        cohort=cohort, dataset=dataset, iteration=iteration + 1, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    data.to_csv(next_data_path)
    col_types.to_csv(next_col_types_path)
