"""Creates a graphical visualization of a clustering"""

from pandas import DataFrame, read_csv, merge
import matplotlib.pyplot as plt

from handler.utils import PTID_COL, CLUSTER_ID_COL


def plot_clustering_handler(clustering_path: str, data_path: str):
    """Main method of this module"""

    # Attach the cluster IDs to the data
    data: DataFrame = read_csv(data_path)
    clustering: DataFrame = read_csv(clustering_path)
    data: DataFrame = merge(data, clustering, on=PTID_COL, how='inner')

    # Now separate feature 1, feature 2 (there should only be 2 features used), and the cluster IDs
    del data[PTID_COL]
    cluster_ids: list = list(data[CLUSTER_ID_COL])
    del data[CLUSTER_ID_COL]
    assert data.shape[-1] == 2
    feat1, feat2 = tuple(data.columns)
    feats1: list = list(data[feat1])
    feats2: list = list(data[feat2])

    # Plot the data
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scatter = ax.scatter(feats1, feats2, c=cluster_ids, s=50)
    ax.set_xlabel(feat1)
    ax.set_ylabel(feat2)
    plt.colorbar(scatter)
    plt.savefig('clustering-plot.png')
