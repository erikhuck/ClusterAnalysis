"""Combines the data sets into one"""

from os.path import join

from pandas import DataFrame, merge, concat, read_csv, Series
from handler.utils import PTID_COL, BASE_DATA_PATH, BASE_COL_TYPES_PATH, DEBUG_IDENTIFIER, get_del_ptid_col


def combine_handler(cohort: str, dataset: str, mri_path: str, do_debug: bool):
    """Main method of this module"""

    phenotypes_data_name: str = 'phenotypes'
    expression_data_name: str = 'expression'
    mri_data_name: str = 'mri'

    if do_debug:
        expression_data_name: str = DEBUG_IDENTIFIER + expression_data_name
        mri_data_name: str = DEBUG_IDENTIFIER + mri_data_name

    # Load the data
    phenotypes_data, phenotypes_col_types = load_data(data_name=phenotypes_data_name, cohort=cohort)
    expression_data, expression_col_types = load_data(data_name=expression_data_name, cohort=cohort)

    if mri_path is not None:
        mri_data: DataFrame = read_csv(mri_path)
        mri_col_types_path: list = mri_path.split('/')
        mri_col_types_path[-1] = mri_col_types_path[-1].replace('data', 'col-types')
        mri_col_types_path: str = join(*mri_col_types_path)
        mri_col_types: DataFrame = read_csv(mri_col_types_path)
    else:
        mri_data, mri_col_types = load_data(data_name=mri_data_name, cohort=cohort)

    # Merge the data sets by PTID
    combined_data: DataFrame = merge(phenotypes_data, expression_data, on=PTID_COL, how='inner')
    combined_data: DataFrame = merge(combined_data, mri_data, on=PTID_COL, how='inner')

    # Remove the columns that only have one unique value as a result of the merge
    combined_data: DataFrame = remove_cols_of_one_unique_val(data=combined_data)

    # Normalize the data again since the minimum and maximum column values may have been changed in the merge
    # This will affect the nominal columns too but that's okay since their values are still distinguishable
    combined_data = normalize(df=combined_data)

    # Likewise, combine the column types data frames
    col_types: DataFrame = concat([phenotypes_col_types, expression_col_types, mri_col_types], axis=1)

    # Filter the column types based on what features remain after the merge
    cols_left: list = list(combined_data.columns)
    cols_left.remove(PTID_COL)
    col_types: DataFrame = col_types[cols_left]

    # Save the combined data set
    combined_data.to_csv(BASE_DATA_PATH.format(cohort, dataset), index=False)
    col_types.to_csv(BASE_COL_TYPES_PATH.format(cohort, dataset), index=False)


def load_data(data_name: str, cohort: str) -> tuple:
    """Loads one of the data sets to be combined"""

    data_path: str = BASE_DATA_PATH.format(cohort, data_name)
    data: DataFrame = read_csv(data_path)
    col_types_path: str = BASE_COL_TYPES_PATH.format(cohort, data_name)
    col_types: DataFrame = read_csv(col_types_path)
    return data, col_types


def normalize(df: DataFrame) -> DataFrame:
    """Normalizes the data"""

    ptid_col: DataFrame = get_del_ptid_col(df)
    df: DataFrame = (df - df.min(axis=0)) / (df.max(axis=0) - df.min(axis=0))
    df: DataFrame = concat([ptid_col, df], axis=1)
    return df


def remove_cols_of_one_unique_val(data: DataFrame) -> DataFrame:
    """Removes columns from the current data set that only have one unique value as a result of the filtering"""

    for col_name in list(data):
        col: Series = data[col_name]

        if len(col.unique()) == 1:
            del data[col_name]

    return data
