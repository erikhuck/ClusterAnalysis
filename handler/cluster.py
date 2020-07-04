"""Runs a clustering algorithm on a data set and labels the data"""

from pandas import read_csv, DataFrame, concat
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score
from numpy import ndarray

from handler.utils import CSV_PATH, PTID_COL, get_del_col, CLUSTERING_PATH


def cluster_handler(n_clusters: int, cohort: str):
    """Main function of this module"""

    data: DataFrame = read_csv(CSV_PATH.format(cohort))
    ptid_col: DataFrame = get_del_col(data_set=data, col_types=None, col_name=PTID_COL)
    data: ndarray = data.to_numpy()
    model = SpectralClustering(
        n_clusters=n_clusters, affinity='nearest_neighbors', assign_labels='kmeans', random_state=0
    )
    labels = model.fit_predict(data)
    clustering_score: float = silhouette_score(data, labels)
    print('Clustering Score:', clustering_score)

    # Save the clustering
    labels: DataFrame = DataFrame(labels, columns=['CLUSTER_ID'])
    clustering: DataFrame = concat([ptid_col, labels], axis=1)
    clustering.to_csv(CLUSTERING_PATH.format(cohort), index=False)
