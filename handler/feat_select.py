"""Selects features from an ARFF using a WEKA feature selection algorithm"""

from os import popen
from pandas import DataFrame, concat

from handler.utils import ARFF_PATH, get_data_path, get_col_types_path, get_data, get_del_ptid_col


def feat_select_handler(cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int):
    """Main method of this module"""

    n_kept_feats_decay: float = 0.9

    # We need to get the previous data now because n_kept_feats will change after selecting features
    data, col_types, n_kept_feats = get_data(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )

    # Run the feature selection WEKA algorithm on the ARFF
    arff_path: str = ARFF_PATH.format(cohort, dataset, iteration, n_kept_feats, n_clusters)
    n_kept_feats: int = int(n_kept_feats * n_kept_feats_decay)
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

    # Select the features from the previous data
    ptid_col: DataFrame = get_del_ptid_col(data_set=data)
    data: DataFrame = data[feats_to_keep].copy()
    data: DataFrame = concat([ptid_col, data], axis=1)
    col_types: DataFrame = col_types[feats_to_keep].copy()
    next_data_path: str = get_data_path(
        cohort=cohort, dataset=dataset, iteration=iteration + 1, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    next_col_types_path: str = get_col_types_path(
        cohort=cohort, dataset=dataset, iteration=iteration + 1, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    data.to_csv(next_data_path, index=False)
    col_types.to_csv(next_col_types_path, index=False)
