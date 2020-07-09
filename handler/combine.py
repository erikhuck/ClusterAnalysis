"""Combines the data sets into one"""

from pandas import DataFrame, merge, concat, read_csv
from handler.utils import (
    PTID_COL, get_del_col, normalize, NUMERIC_COL_TYPE, PHENOTYPES_PATH, PHENOTYPES_COL_TYPES_PATH, COMBINED_PATH,
    COMBINED_COL_TYPES_PATH
)


def combine_handler(cohort: str):
    """Main method of this module"""

    # Handle the MRI data
    # TODO: mri_data, mri_col_types, n_mri_cols = process_numeric_data(cohort=cohort, csv='mri)

    # Handle the expression data
    expression_data, expression_col_types, n_expression_cols = process_numeric_data(cohort=cohort, csv='expression')

    # Handle the phenotype data
    phenotype_data, phenotype_col_types, n_phenotype_cols = load_phenotype_data(cohort=cohort)

    # Merge the data sets by PTID
    combined_data: DataFrame = merge(expression_data, phenotype_data, on=PTID_COL, how='inner')
    assert combined_data.shape[-1] == n_expression_cols + n_phenotype_cols + 1  # Plus one for the ptids TODO: MRIs too
    # TODO: combined_data: DataFrame = merge(combined_data, mri_data, on=PTID_COL, how='inner')

    # Likewise, combine the column types data frames
    col_types: DataFrame = concat([expression_col_types, phenotype_col_types], axis=1)
    # TODO: col_types: DataFrame = concat([col_types, mri_col_types], axis=1)

    combined_data.to_csv(COMBINED_PATH.format(cohort), index=False)
    col_types.to_csv(COMBINED_COL_TYPES_PATH.format(cohort), index=False)


def process_numeric_data(cohort: str, csv: str):
    """Processes a data set that is complete, needs no targets, and entirely numeric"""

    data_path: str = 'raw-data/{}/{}.csv'.format(cohort, csv)
    data: DataFrame = read_csv(data_path, low_memory=False)
    ptid_col: DataFrame = get_del_col(data_set=data, col_types=None, col_name=PTID_COL)
    data: DataFrame = normalize(df=data)
    n_cols: int = data.shape[-1]
    col_types: list = [NUMERIC_COL_TYPE] * n_cols
    col_types: DataFrame = DataFrame(data=[col_types], columns=list(data))
    data: DataFrame = concat([ptid_col, data], axis=1)
    return data, col_types, n_cols


def load_phenotype_data(cohort: str):
    """Loads the phenotypic data that was processed by the phenotypes handler"""

    phenotypes_path: str = PHENOTYPES_PATH.format(cohort)
    phenotype_data: DataFrame = read_csv(phenotypes_path)
    col_types_path: str = PHENOTYPES_COL_TYPES_PATH.format(cohort)
    phenotype_col_types: DataFrame = read_csv(col_types_path)
    n_phenotype_cols: int = phenotype_data.shape[-1] - 1
    return phenotype_data, phenotype_col_types, n_phenotype_cols
