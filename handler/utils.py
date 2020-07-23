"""Contains functionality data shared between handlers"""

from pandas import DataFrame, read_csv

PTID_COL: str = 'PTID'
CLUSTERING_PATH: str = 'clean-data/{}/{}/iter{}/clustering-{}-{}-{}.csv'
ARFF_PATH: str = 'clean-data/{}/{}/iter{}/data-{}-{}.arff'
DATA_PATH: str = 'clean-data/{}/{}/iter{}/data-{}-{}.csv'
COL_TYPES_PATH: str = 'clean-data/{}/{}/iter{}/col-types-{}-{}.csv'
BASE_DATA_PATH: str = 'prepared-data/{}/{}.csv'
BASE_COL_TYPES_PATH: str = 'prepared-data/{}/{}-col-types.csv'
DEBUG_IDENTIFIER: str = 'dbg-'
CLUSTER_ID_COL: str = 'CLUSTER_ID'
NUMERIC_COL_TYPE: str = 'numeric'
NOMINAL_COL_TYPE: str = 'nominal'


def _get_path(
        cohort: str, dataset: str, iteration: int, n_kept_feats: int, n_clusters: int, base_path: str, path: str
) -> str:
    """Gets the path to either a column types CSV or a data CSV for a given iteration in the pipeline"""

    if iteration == 0:
        assert n_kept_feats is None
        data_path: str = base_path.format(cohort, dataset)
    else:
        assert iteration > 0
        data_path: str = path.format(cohort, dataset, iteration - 1, n_kept_feats, n_clusters)

    return data_path


def get_data_path(cohort: str, dataset: str, iteration: int, n_kept_feats: int, n_clusters: int) -> str:
    """Gets the data set for a given iteration of the pipeline"""

    return _get_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters,
        base_path=BASE_DATA_PATH, path=DATA_PATH
    )


def get_col_types_path(cohort: str, dataset: str, iteration: int, n_kept_feats: int, n_clusters: int) -> str:
    """Gets the columns types data frame for a given iteration in the pipeline"""

    return _get_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters,
        base_path=BASE_COL_TYPES_PATH, path=COL_TYPES_PATH
    )


def get_data(cohort: str, dataset: str, iteration: int, n_kept_feats: int, n_clusters: int) -> tuple:
    """Gets a data set, it's column types and n_kept_feats if at the beginning of the clustering pipeline"""

    data_path: str = get_data_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    data: DataFrame = read_csv(data_path)

    col_types_path: str = get_col_types_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    col_types: DataFrame = read_csv(col_types_path)

    if n_kept_feats is None:
        n_kept_feats: int = col_types.shape[-1]
    else:
        # TODO: It appears that passing in --n-kept-feats is pointless
        assert n_kept_feats == col_types.shape[-1]

    return data, col_types, n_kept_feats


def get_del_ptid_col(data_set: DataFrame) -> DataFrame:
    """Obtains and deletes a column from the data set"""

    col: DataFrame = data_set[[PTID_COL]].copy()
    del data_set[PTID_COL]

    return col
