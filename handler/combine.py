"""Combines the data sets into one"""

from pandas import DataFrame, merge, concat, read_csv
from handler.utils import PTID_COL, BASE_DATA_PATH, BASE_COL_TYPES_PATH, DEBUG_IDENTIFIER


def combine_handler(cohort: str, do_debug: bool):
    """Main method of this module"""

    dataset_name: str = 'combined'
    phenotypes_data_name: str = 'phenotypes'
    expression_data_name: str = 'expression'
    mri_data_name: str = 'mri'

    if do_debug:
        dataset_name: str = DEBUG_IDENTIFIER + dataset_name
        expression_data_name: str = DEBUG_IDENTIFIER + expression_data_name
        mri_data_name: str = DEBUG_IDENTIFIER + mri_data_name

    # Load the data
    phenotypes_data, phenotypes_col_types = load_data(data_name=phenotypes_data_name, cohort=cohort)
    expression_data, expression_col_types = load_data(data_name=expression_data_name, cohort=cohort)
    # TODO: Load the feature selected MRI data

    # Merge the data sets by PTID
    combined_data: DataFrame = merge(phenotypes_data, expression_data, on=PTID_COL, how='inner')
    # TODO: combined_data: DataFrame = merge(combined_data, mri_data, on=PTID_COL, how='inner')

    # Likewise, combine the column types data frames
    # TODO: col_types: DataFrame = concat([phenotypes_col_types, expression_col_types, mri_col_types], axis=1)
    col_types: DataFrame = concat([phenotypes_col_types, expression_col_types], axis=1)

    # Save the CSV that will serve as the basis for future feature reduction
    combined_data.to_csv(BASE_DATA_PATH.format(cohort, dataset_name), index=False)
    col_types.to_csv(BASE_COL_TYPES_PATH.format(cohort, dataset_name), index=False)


def load_data(data_name: str, cohort: str) -> tuple:
    """Loads one of the data sets to be combined"""

    data_path: str = BASE_DATA_PATH.format(cohort, data_name)
    data: DataFrame = read_csv(data_path)
    col_types_path: str = BASE_COL_TYPES_PATH.format(cohort, data_name)
    col_types: DataFrame = read_csv(col_types_path)
    return data, col_types
