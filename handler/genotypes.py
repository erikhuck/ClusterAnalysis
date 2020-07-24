"""Classifies clustering labels based on genotypic data"""

from pandas import read_csv, DataFrame, merge

from handler.utils import get_data_path, PTID_COL


def genotypes_handler(cohort: str, dataset: str, clustering_path: str):
    """Main method of this module"""

    # Get the clustering the labels of which will act as classification targets
    clustering: DataFrame = read_csv(clustering_path)

    # Get the genotype data set path, the last 3 parameters are 0 or None because we're not using the pipeline currently
    data_path: str = get_data_path(
        cohort=cohort, dataset=dataset, iteration=0, n_kept_feats=None, n_clusters=None
    )

    # TODO: Not tested below this point
    data: DataFrame = read_csv(data_path)
    data: DataFrame = merge(data, clustering, on=PTID_COL, how='inner')
