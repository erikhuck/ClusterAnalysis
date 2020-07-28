"""Runs a clustering algorithm on a data set and labels the data"""

from pandas import DataFrame, concat, Series, get_dummies
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score
from numpy import ndarray

from handler.utils import (
    get_del_ptid_col, CLUSTERING_PATH, CLUSTER_ID_COL, get_data, NOMINAL_COL_TYPE, NUMERIC_COL_TYPE
)


def cluster_handler(
    cohort: str, dataset: str, cluster_method: str, n_clusters: int, iteration: int, n_kept_feats: int
):
    """Main function of this module"""

    data, ptid_col, n_kept_feats = get_data_set(
        cohort=cohort, dataset=dataset, cluster_method=cluster_method, n_clusters=n_clusters, iteration=iteration,
        n_kept_feats=n_kept_feats
    )

    model = SpectralClustering(
        n_clusters=n_clusters, affinity=cluster_method, assign_labels='kmeans', random_state=0
    )
    labels: ndarray = model.fit_predict(data)
    clustering_score: float = silhouette_score(data, labels)
    clustering_score: float = round(clustering_score, 2)
    print(clustering_score)

    labels: DataFrame = DataFrame(labels, columns=[CLUSTER_ID_COL])
    clustering: DataFrame = concat([ptid_col, labels], axis=1)

    # Save the clustering
    clustering_path: str = CLUSTERING_PATH.format(
        cohort, dataset, cluster_method, n_clusters, iteration, n_kept_feats, clustering_score
    )
    clustering.to_csv(clustering_path, index=False)


def get_data_set(
    cohort: str, dataset: str, cluster_method: str, n_clusters: int, iteration: int, n_kept_feats: int
) -> tuple:
    """Creates the final data set from the selected features and one-hot encoded nominal columns"""

    data, col_types, n_kept_feats = get_data(
        cohort=cohort, dataset=dataset, cluster_method=cluster_method, n_clusters=n_clusters, iteration=iteration,
        n_kept_feats=n_kept_feats
    )

    # Temporarily take out the patient id column
    ptid_col: DataFrame = get_del_ptid_col(data_set=data)

    # Get the nominal data and one hot encode it
    nominal_data, nominal_cols = get_cols_by_type(data_set=data, data_types=col_types, col_type=NOMINAL_COL_TYPE)

    if nominal_data.shape[-1] > 0:
        nominal_data: DataFrame = get_dummies(nominal_data, columns=nominal_cols, dummy_na=False)

    # Get the numeric data
    numeric_data, _ = get_cols_by_type(data_set=data, data_types=col_types, col_type=NUMERIC_COL_TYPE)

    # Combine the numeric and nominal columns into one complete data set
    data: DataFrame = concat([numeric_data, nominal_data], axis=1)

    return data.to_numpy(), ptid_col, n_kept_feats


def get_cols_by_type(data_set: DataFrame, data_types: DataFrame, col_type: str) -> tuple:
    """Gets the columns and column names of a given type"""

    col_bools: Series = data_types.loc[0] == col_type
    cols: Series = data_types[col_bools.index[col_bools]]
    cols: list = list(cols)
    data: DataFrame = data_set[cols]
    return data, cols
