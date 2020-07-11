"""Runs a clustering algorithm on a data set and labels the data"""

from pandas import read_csv, DataFrame, concat
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score
from numpy import ndarray

from handler.utils import CSV_PATH, PTID_COL, get_del_col, CLUSTERING_PATH, CLUSTER_ID_COL


def cluster_handler(cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int):
    """Main function of this module"""

    data_path: str = CSV_PATH.format(cohort, dataset, iteration, n_kept_feats, n_clusters)
    data: DataFrame = read_csv(data_path)
    ptid_col: DataFrame = get_del_col(data_set=data, col_types=None, col_name=PTID_COL)
    data: ndarray = data.to_numpy()
    model = SpectralClustering(
        n_clusters=n_clusters, affinity='nearest_neighbors', assign_labels='kmeans', random_state=0
    )
    labels = model.fit_predict(data)
    clustering_score: float = silhouette_score(data, labels)
    clustering_score: float = round(clustering_score, 2)
    print(clustering_score)

    # Save the clustering
    labels: DataFrame = DataFrame(labels, columns=[CLUSTER_ID_COL])
    clustering: DataFrame = concat([ptid_col, labels], axis=1)
    clustering_path: str = CLUSTERING_PATH.format(
        cohort, dataset, iteration, n_kept_feats, n_clusters, clustering_score
    )
    clustering.to_csv(clustering_path, index=False)
