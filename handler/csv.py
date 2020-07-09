"""Takes the features selected by WEKA to create a CSV data set for deep learning"""

from pandas import concat, DataFrame, get_dummies, read_csv

from handler.utils import (
    CSV_PATH, PTID_COL, get_del_col, COMBINED_PATH, COMBINED_COL_TYPES_PATH, get_cols_by_type, NOMINAL_COL_TYPE,
    NUMERIC_COL_TYPE
)


def csv_handler(cohort: str, kept_feats: str):
    """Main function of this module"""

    # Load the initial data
    col_types_path: str = COMBINED_COL_TYPES_PATH.format(cohort)
    col_types: DataFrame = read_csv(col_types_path)
    data_path: str = COMBINED_PATH.format(cohort)
    data: DataFrame = read_csv(data_path)

    # Construct the final data set using only the selected features
    data: DataFrame = get_data_set(data=data, col_types=col_types, kept_feats=kept_feats)

    # Save the CSV
    csv_path: str = CSV_PATH.format(cohort)
    data.to_csv(csv_path, index=False)


def get_data_set(data: DataFrame, col_types: DataFrame, kept_feats: str) -> DataFrame:
    """Creates the final data set from the selected features and one-hot encoded nominal columns"""

    # Temporarily take out the patient id column
    ptid_col: DataFrame = get_del_col(data_set=data, col_types=None, col_name=PTID_COL)

    if kept_feats is not None:
        # Load in the columns that were selected by a feature selection algorithm
        with open(kept_feats, 'r') as f:
            kept_feats: str = f.read()

        kept_feats: list = kept_feats.split('\n')
        kept_feats.remove('')
        assert '' not in kept_feats

        # Splice out only the selected features
        data: DataFrame = data[kept_feats].copy()
        col_types: DataFrame = col_types[kept_feats].copy()

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
