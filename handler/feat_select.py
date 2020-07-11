"""Selects features from an ARFF using a WEKA feature selection algorithm"""

from os import popen

from handler.utils import KEPT_FEATS_PATH, ARFF_PATH


def feat_select_handler(cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int):
    """Main method of this module"""

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
    kept_feats_path: str = KEPT_FEATS_PATH.format(cohort, dataset, iteration, n_kept_feats, n_clusters)

    # Save the kept features
    with open(kept_feats_path, 'w') as f:
        for feat in feats_to_keep:
            f.write(feat + '\n')

