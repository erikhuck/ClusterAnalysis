from pandas import concat
from pandas import DataFrame
from pandas import get_dummies
from pandas import read_csv
from pandas import Series
from numpy import ndarray
from numpy import concatenate
# noinspection PyProtectedMember
from sklearn.impute._iterative import IterativeImputer


def get_cols_by_type(data_set: DataFrame, data_types: DataFrame, col_type: str) -> tuple:
    col_bools: Series = data_types.loc[0] == col_type
    cols: Series = data_types[col_bools.index[col_bools]]
    cols: list = list(cols)
    data: DataFrame = data_set[cols]
    return data, cols


def normalize(df: DataFrame) -> DataFrame:
    df: DataFrame = (df - df.min(axis=0)) / (df.max(axis=0) - df.min(axis=0))
    return df


def clean_data(data_path: str, data_types_path: str):
    # Load in the raw data set and the table that indicates the data type of each column
    data_set: DataFrame = read_csv(data_path, low_memory=False)
    data_types: DataFrame = read_csv(data_types_path)

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

    # Concatenate the nominal columns to the numeric columns so the nominal columns can be used in the imputation algorithm
    data_to_impute: ndarray = concatenate((numeric_data, nominal_data.to_numpy()), axis=1)

    del numeric_data

    # Impute missing numeric values
    imputer: IterativeImputer = IterativeImputer(verbose=2, random_state=0, add_indicator=False, max_iter=2)
    imputed_data: ndarray = imputer.fit_transform(data_to_impute)

    # Separate the numeric columns from the nominal columns used to impute
    numeric_data: ndarray = imputed_data[:, :n_numeric_cols]

    del imputed_data
    numeric_data: DataFrame = DataFrame(data=numeric_data, columns=numeric_cols)

    # Recombine the nominal data with the numeric data
    data: DataFrame = concat([numeric_data, nominal_data], axis=1)
    data.to_csv('data.csv', index=False)
