"""Takes the features selected by WEKA to create a CSV data set for deep learning"""

from pandas import concat, DataFrame, get_dummies, read_csv

from handler.utils import (
    CSV_PATH, PTID_COL, get_del_col, BASE_CSV_PATH, COL_TYPES_PATH, get_cols_by_type, NOMINAL_COL_TYPE,
    NUMERIC_COL_TYPE, KEPT_FEATS_PATH, get_kept_feats
)


def csv_handler(cohort: str, iteration: int, dataset: str, n_kept_feats: int, n_clusters: int, clustering_score: str):
    """Main function of this module"""

    # Load the initial data
    col_types_path: str = COL_TYPES_PATH.format(cohort, dataset)
    col_types: DataFrame = read_csv(col_types_path)
    data_path: str = BASE_CSV_PATH.format(cohort, dataset)
    data: DataFrame = read_csv(data_path)

    # Save the CSV
    if iteration == 0:
        # All the features were kept because this is the first iteration
        assert n_kept_feats is None
        n_kept_feats: int = len(list(col_types))
        print(n_kept_feats)
        kept_feats_path = None
    else:
        # There were features selected in the previous iteration
        kept_feats_path: str = KEPT_FEATS_PATH.format(
            cohort, iteration - 1, dataset, n_kept_feats, n_clusters, clustering_score
        )

    # Construct the final data set using only the selected features
    data: DataFrame = get_data_set(data=data, col_types=col_types, kept_feats_path=kept_feats_path)

    csv_path: str = CSV_PATH.format(cohort, iteration, dataset, n_kept_feats, n_clusters, clustering_score)
    data.to_csv(csv_path, index=False)


def get_data_set(data: DataFrame, col_types: DataFrame, kept_feats_path: str) -> DataFrame:
    """Creates the final data set from the selected features and one-hot encoded nominal columns"""

    # Temporarily take out the patient id column
    ptid_col: DataFrame = get_del_col(data_set=data, col_types=None, col_name=PTID_COL)

    if kept_feats_path is not None:
        data, col_types = get_kept_feats(kept_feats_path=kept_feats_path, data=data, col_types=col_types)

    # Get the nominal data and one hot encode it
    nominal_data, nominal_cols = get_cols_by_type(data_set=data, data_types=col_types, col_type=NOMINAL_COL_TYPE)

    if nominal_data.shape[-1] > 0:
        nominal_data: DataFrame = get_dummies(nominal_data, columns=nominal_cols, dummy_na=False)
    
    # Get the numeric data
    numeric_data, _ = get_cols_by_type(data_set=data, data_types=col_types, col_type=NUMERIC_COL_TYPE)

    # Combine the numeric and nominal columns into one complete data set
    data: DataFrame = concat([numeric_data, nominal_data], axis=1)

    # Merge the PTID column back in
    data: DataFrame = concat([ptid_col, data], axis=1)

    return data
