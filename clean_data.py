"""Prepares the data for a machine learning algorithm"""

from pandas import concat, DataFrame, get_dummies, factorize, read_csv, Series
from numpy import concatenate, ndarray, nanmin, nanmax
# noinspection PyUnresolvedReferences
from sklearn.experimental import enable_iterative_imputer
# noinspection PyUnresolvedReferences,PyProtectedMember
from sklearn.impute import IterativeImputer


def get_cols_by_type(data_set: DataFrame, data_types: DataFrame, col_type: str) -> tuple:
    """Gets the columns and column names of a given type"""

    col_bools: Series = data_types.loc[0] == col_type
    cols: Series = data_types[col_bools.index[col_bools]]
    cols: list = list(cols)
    data: DataFrame = data_set[cols]
    return data, cols


def normalize(df: DataFrame) -> DataFrame:
    """Normalizes numeric columns in a data frame"""

    df: DataFrame = (df - df.min(axis=0)) / (df.max(axis=0) - df.min(axis=0))
    return df


def clean_data(data_path: str, data_types_path: str):
    """Main function of this module"""

    # Constants
    max_iter: int = 2
    n_nearest_features: int = 200
    target_col: str = 'CDCOMMUN'
    impute_seed: int = 0

    # Load in the raw data set and the table that indicates the data type of each column
    data_set: DataFrame = read_csv(data_path, low_memory=False)
    data_types: DataFrame = read_csv(data_types_path)

    # Remove rows with unknown targets
    data_set: DataFrame = data_set[data_set[target_col].notna()].reset_index()

    # Separate the targets
    targets: Series = data_set[target_col]
    del data_set[target_col]
    del data_types[target_col]

    # Ordinal encode the targets
    targets, _ = factorize(targets)

    # Combine the highest target category with the second highest category
    max_cat: int = targets.max()
    targets[targets == max_cat] = max_cat - 1

    targets: DataFrame = DataFrame(targets, columns=[target_col])

    # Get the nominal columns and column names
    nominal_data, nominal_cols = get_cols_by_type(data_set=data_set, data_types=data_types, col_type='nominal')
    
    # One hot encode the nominal values, treating nan values as an extra category
    nominal_data: DataFrame = get_dummies(nominal_data, columns=nominal_cols, dummy_na=True)

    # Get the numeric columns and column names
    numeric_data, numeric_cols = get_cols_by_type(data_set=data_set, data_types=data_types, col_type='numeric')

    # Normalize the numeric columns
    numeric_data: DataFrame = normalize(df=numeric_data)

    numeric_data: ndarray = numeric_data.to_numpy()
    n_numeric_cols: int = numeric_data.shape[1]

    # Combine the nominal columns with the numeric so the nominal columns can be used in the imputation
    data_to_impute: ndarray = concatenate((numeric_data, nominal_data.to_numpy()), axis=1)

    # Impute missing numeric values
    imputer: IterativeImputer = IterativeImputer(
        verbose=2, random_state=impute_seed, max_iter=max_iter, max_value=nanmax(data_to_impute),
        min_value=nanmin(data_to_impute), n_nearest_features=n_nearest_features
    )
    imputed_data: ndarray = imputer.fit_transform(data_to_impute)

    # Separate the numeric columns from the nominal columns used to impute
    numeric_data: ndarray = imputed_data[:, :n_numeric_cols]

    numeric_data: DataFrame = DataFrame(data=numeric_data, columns=numeric_cols)

    # Recombine the nominal data with the numeric data and the targets
    data: DataFrame = concat([numeric_data, nominal_data, targets], axis=1)
    data.to_csv('data.csv', index=False)
