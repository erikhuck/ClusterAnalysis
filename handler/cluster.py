"""Runs a clustering algorithm on a data set and labels the data"""

from pandas import read_csv, DataFrame
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score
from numpy import ndarray


def cluster_handler(n_clusters: int, data_path: str):
    """Main function of this module"""

    data: DataFrame = read_csv(data_path)
    data: ndarray = data.to_numpy()
    model = SpectralClustering(n_clusters=n_clusters, affinity='nearest_neighbors', assign_labels='kmeans')
    labels = model.fit_predict(data)
    clustering_score: float = silhouette_score(data, labels)
    print('Clustering Score:', clustering_score)
