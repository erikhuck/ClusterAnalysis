"""Counts the number of individuals in each category of a given variate"""

from pandas import DataFrame, read_csv
from pickle import load

from handler.utils import PTID_COL, CLUSTER_ID_COL


def counts_handler(clustering_path: str, feat_map_path: str):
    """Main method of this module"""

    clustering: DataFrame = read_csv(clustering_path)
    feat_map: dict = load(open(feat_map_path, 'rb'))
    clustering: dict = convert_clustering_to_dict(clustering=clustering)
    counts: dict = {}

    for ptid, clusterid in clustering.items():
        variant_category: object = feat_map[ptid]

        # Add the variant that corresponds to this cluster ID
        if clusterid in counts:
            cluster_counts: dict = counts[clusterid]

            if variant_category in cluster_counts:
                cluster_counts[variant_category] += 1
            else:
                cluster_counts[variant_category] = 1
        else:
            counts[clusterid] = {variant_category: 1}

    grand_total: int = get_grand_total(counts=counts)
    assert grand_total == len(clustering)

    for clusterid, cluster_counts in counts.items():
        # Get the total count
        cluster_total: int = get_cluster_total(cluster_counts=cluster_counts)

        cluster_print: str = 'Cluster {}: {}/{} ({:.2f}%)'.format(
            clusterid, cluster_total, grand_total, cluster_total / grand_total * 100.0
        )
        print(cluster_print)

        for variant_category, count in cluster_counts.items():
            variant_print: str = '\t{}: {}/{} ({:.2f}%)'.format(
                variant_category, count, cluster_total, count / cluster_total * 100.0
            )
            print(variant_print)

        print()


def convert_clustering_to_dict(clustering: DataFrame) -> dict:
    """Converts a clustering from data frame format to a dictionary format"""

    ptids: list = list(clustering[PTID_COL])
    clusterids: list = list(clustering[CLUSTER_ID_COL])
    clustering: dict = {}

    for ptid, clusterid in zip(ptids, clusterids):
        clustering[ptid] = clusterid

    return clustering


def get_grand_total(counts: dict) -> int:
    """Computes the total number of samples in the entire clustering"""

    grand_total: int = 0

    for cluster_counts in counts.values():
        cluster_total: int = get_cluster_total(cluster_counts=cluster_counts)
        grand_total += cluster_total

    return grand_total


def get_cluster_total(cluster_counts: dict):
    """Computes the total number of samples in a cluster"""

    cluster_total: int = 0

    for count in cluster_counts.values():
        cluster_total += count

    return cluster_total
