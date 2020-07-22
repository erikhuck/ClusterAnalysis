"""Processes the data and converts it to an ARFF file"""

from pandas import DataFrame, read_csv, Series, merge

from handler.utils import (
    ARFF_PATH, PTID_COL, CLUSTERING_PATH, CLUSTER_ID_COL, NUMERIC_COL_TYPE, get_data_path, get_col_types_path
)


def arff_handler(cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int, clustering_score: str):
    """Main function of this module"""

    # Load the data
    data_path: str = get_data_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    data: DataFrame = read_csv(data_path)

    if n_kept_feats is None:
        n_kept_feats: int = data.shape[-1]

    # Load the clustering
    clustering_path: str = CLUSTERING_PATH.format(
        cohort, dataset, iteration, n_kept_feats, n_clusters, clustering_score
    )
    clustering: DataFrame = read_csv(clustering_path)

    # Combine the data with the clustering labels
    data: DataFrame = merge(data, clustering, on=PTID_COL, how='inner')

    # Since the clustering labels are for selecting features, we do not want to include the patient IDs in the ARFF
    del data[PTID_COL]

    col_types_path: str = get_col_types_path(
        cohort=cohort, dataset=dataset, iteration=iteration, n_kept_feats=n_kept_feats, n_clusters=n_clusters
    )
    col_types: DataFrame = read_csv(col_types_path)

    # Convert the data to ARFF format and save it as an ARFF file
    arff_path: str = ARFF_PATH.format(cohort, dataset, iteration, n_kept_feats, n_clusters)
    save_data(arff_path=arff_path, arff_data=data, col_types=col_types, target_col=CLUSTER_ID_COL, cohort=cohort)


def save_data(arff_path: str, arff_data: DataFrame, col_types: DataFrame, target_col: str, cohort: str):
    """Stores the data on disk as an ARFF and a CSV"""

    # Save the data of the ARFF as a CSV so the header can be added to it
    arff_data.to_csv(arff_path, index=False)

    # Open the ARFF as a text file to edit
    with open(arff_path, 'r') as f:
        arff: str = f.read()

    # Remove the first line
    arff: list = arff.split('\n')
    arff: list = arff[1:]

    # Remove empty strings
    while '' in arff:
        arff.remove('')

    # Make the header
    header: list = ['@RELATION {}'.format(cohort.upper())]

    col_names: list = list(arff_data)
    for col_name in col_names:
        line: str = '@ATTRIBUTE {}'.format(col_name)

        if col_name == target_col:
            is_numeric: bool = False
        else:
            is_numeric: bool = col_types.loc[0, col_name] == NUMERIC_COL_TYPE

        if is_numeric:
            line += ' ' + 'NUMERIC'
        else:
            col: Series = arff_data[col_name]
            categories: set = set(col.unique())
            line += ' ' + str(categories).replace(' ', '')

        header.append(line)

    header.append('@DATA')

    # Attach the header to the ARFF
    header.extend(arff)
    arff: list = header

    # Rewrite the ARFF with the header included
    with open(arff_path, 'w') as f:
        for line in arff:
            f.write(line + '\n')
