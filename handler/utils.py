"""Contains functionality data shared between handlers"""

from pandas import DataFrame, Series

PTID_COL: str = 'PTID'
CSV_PATH: str = 'clean-data/{}/{}/iter{}/data-{}-{}.csv'
CLUSTERING_PATH: str = 'clean-data/{}/{}/iter{}/clustering-{}-{}-{}.csv'
ARFF_PATH: str = 'clean-data/{}/{}/iter{}/data-{}-{}.arff'
KEPT_FEATS_PATH: str = 'clean-data/{}/{}/iter{}/kept_feats-{}-{}.txt'
PTID_TO_CDR_PATH: str = 'intermediate-data/{}/ptid-to-cdr.p'
PHENOTYPES_PATH: str = 'intermediate-data/{}/phenotypes.csv'
BASE_CSV_PATH: str = 'intermediate-data/{}/{}.csv'
COL_TYPES_PATH: str = 'intermediate-data/{}/{}-col-types.csv'
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


def get_kept_feats(kept_feats_path: str, data: DataFrame, col_types: DataFrame, keep_cluster_id: bool = False) -> tuple:
    """Splices out the features of a data set that are specified"""

    # Load in the columns that were selected by the WEKA feature selection algorithm on the previous iteration
    with open(kept_feats_path, 'r') as f:
        kept_feats: str = f.read()

    kept_feats: list = kept_feats.split('\n')
    kept_feats.remove('')
    assert '' not in kept_feats

    # Splice out only the selected features
    col_types: DataFrame = col_types[kept_feats].copy()

    if keep_cluster_id:
        kept_feats.append(CLUSTER_ID_COL)

    data: DataFrame = data[kept_feats].copy()
    return data, col_types


def get_numeric_col_types(columns: list) -> DataFrame:
    """Gets the column types for a numeric data set"""

    n_cols: int = len(columns)
    col_types: list = [NUMERIC_COL_TYPE] * n_cols
    col_types: DataFrame = DataFrame(data=[col_types], columns=columns)
    return col_types
