"""Creates a smaller data set from a larger one for the purpose of quicker debugging"""

from pandas import DataFrame, read_csv, concat
from numpy.random import shuffle, seed

from handler.utils import BASE_DATA_PATH, BASE_COL_TYPES_PATH, get_del_ptid_col, DEBUG_IDENTIFIER


def debug_datasets_handler(cohort: str, dataset: str):
    """Main method of this module"""

    n_debug_cols: int = 1000
    genotypes_dataset: str = 'genotypes'

    # Seed the numpy random number generator for consistency
    seed(0)

    # Read the data
    data_path: str = BASE_DATA_PATH.format(cohort, dataset)
    data: DataFrame = read_csv(data_path)

    ptid_col: DataFrame = get_del_ptid_col(data_set=data)

    # Shuffle the data to get a better distribution of the data set and avoid bias in the columns selected for debugging
    shuffled_cols: list = list(data)
    shuffle(shuffled_cols)
    shuffled_cols: list = shuffled_cols[:n_debug_cols]
    data: DataFrame = data[shuffled_cols]

    # Save the debug data set
    data: DataFrame = concat([ptid_col, data], axis=1)
    dataset: str = DEBUG_IDENTIFIER + dataset
    debug_data_path: str = BASE_DATA_PATH.format(cohort, dataset)
    data.to_csv(debug_data_path, index=False)

    if dataset != genotypes_dataset:
        # Sample the column types accordingly
        col_types_path: str = BASE_COL_TYPES_PATH.format(cohort, dataset)
        col_types: DataFrame = read_csv(col_types_path)
        col_types: DataFrame = col_types[shuffled_cols].copy()
        debug_col_types_path: str = BASE_COL_TYPES_PATH.format(cohort, dataset)
        col_types.to_csv(debug_col_types_path, index=False)

