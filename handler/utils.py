"""Contains functionality data shared between handlers"""

from pandas import DataFrame

PTID_COL: str = 'PTID'
ARFF_PATH: str = 'clean-data/{}/data.arff'
CSV_PATH: str = 'clean-data/{}/data.csv'
PTID_CSV: str = 'clean-data/{}/ptids.csv'
CLUSTERING_PATH: str = 'clean-data/{}/clustering.csv'


def get_del_col(data_set: DataFrame, col_types: DataFrame, col_name: str) -> DataFrame:
    """Obtains and deletes a column from the data set"""

    col: DataFrame = data_set[[col_name]].copy()
    del data_set[col_name]

    if col_types is not None and col_name in col_types:
        del col_types[col_name]

    return col
