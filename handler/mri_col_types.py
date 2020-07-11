"""Makes the column types CSV for the MRI data set"""

from pandas import DataFrame

from handler.utils import COL_TYPES_PATH, get_numeric_col_types


def mri_col_types_handler(cohort: str):
    """Main method of this handler"""

    dataset: str = 'mri'
    columns: list = ['MRI_{}'.format(i) for i in range(8000 * 124)]
    col_types: DataFrame = get_numeric_col_types(columns=columns)
    col_types_path: str = COL_TYPES_PATH.format(cohort, dataset)
    col_types.to_csv(col_types_path, index=False)
