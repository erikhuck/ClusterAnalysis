"""Processes the data and converts it to an ARFF file"""

from pandas import DataFrame, read_csv, Series, merge

from handler.utils import (
    ARFF_PATH, PTID_COL, CLUSTERING_PATH, CLUSTER_ID_COL, NUMERIC_COL_TYPE, BASE_CSV_PATH, COL_TYPES_PATH,
    get_kept_feats, KEPT_FEATS_PATH
)


def arff_handler(cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int, clustering_score: str):
    """Main function of this module"""

    # Combine the data with the clustering labels
    clustering_path: str = CLUSTERING_PATH.format(
        cohort, dataset, iteration, n_kept_feats, n_clusters, clustering_score
    )
    clustering: DataFrame = read_csv(clustering_path)
    data_path: str = BASE_CSV_PATH.format(cohort, dataset)
    data: DataFrame = read_csv(data_path)
    data: DataFrame = merge(data, clustering, on=PTID_COL, how='inner')

    col_types_path: str = COL_TYPES_PATH.format(cohort, dataset)
    col_types: DataFrame = read_csv(col_types_path)

    if iteration == 0:
        # Since the clustering labels are for selecting features, we do not want the patient ids
        del data[PTID_COL]
    else:
        kept_feats_path: str = KEPT_FEATS_PATH.format(cohort, dataset, iteration - 1, n_kept_feats, n_clusters)

        # The patient IDs will be removed too since it is impossible for PTID to be a selected feature
        data, col_types = get_kept_feats(
            kept_feats_path=kept_feats_path, data=data, col_types=col_types, keep_cluster_id=True
        )

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
