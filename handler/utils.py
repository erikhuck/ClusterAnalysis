"""Contains functionality data shared between handlers"""

from pandas import DataFrame, Series

PTID_COL: str = 'PTID'
ARFF_PATH: str = 'clean-data/{}/data.arff'
CSV_PATH: str = 'clean-data/{}/data.csv'
CLUSTERING_PATH: str = 'clean-data/{}/clustering.csv'
PTID_TO_CDR_PATH: str = 'intermediate-data/{}/ptid-to-cdr.p'
PHENOTYPES_PATH: str = 'intermediate-data/{}/phenotypes.csv'
COMBINED_PATH: str = 'intermediate-data/{}/combined.csv'
COMBINED_COL_TYPES_PATH: str = 'intermediate-data/{}/combined-col-types.csv'
PHENOTYPES_COL_TYPES_PATH: str = 'raw-data/{}/phenotype-col-types.csv'
CLUSTER_ID_COL: str = 'CLUSTER_ID'
NUMERIC_COL_TYPE: str = 'numeric'
NOMINAL_COL_TYPE: str = 'nominal'


def get_del_col(data_set: DataFrame, col_types: DataFrame, col_name: str) -> DataFrame:
    """Obtains and deletes a column from the data set"""

    col: DataFrame = data_set[[col_name]].copy()
    del data_set[col_name]

    if col_types is not None and col_name in col_types:
        del col_types[col_name]

    return col


def normalize(df: DataFrame) -> DataFrame:
    """Normalizes numeric columns in a data frame"""

    df: DataFrame = (df - df.min(axis=0)) / (df.max(axis=0) - df.min(axis=0))
    return df


def get_cols_by_type(data_set: DataFrame, data_types: DataFrame, col_type: str) -> tuple:
    """Gets the columns and column names of a given type"""

    col_bools: Series = data_types.loc[0] == col_type
    cols: Series = data_types[col_bools.index[col_bools]]
    cols: list = list(cols)
    data: DataFrame = data_set[cols]
    return data, cols
