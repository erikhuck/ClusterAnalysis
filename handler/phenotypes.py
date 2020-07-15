"""Processes the phenotypic data"""

from pandas import concat, DataFrame, get_dummies, factorize, read_csv, Series
from numpy import concatenate, ndarray, nanmin, nanmax, isnan
from pickle import dump
# noinspection PyUnresolvedReferences
from sklearn.experimental import enable_iterative_imputer
# noinspection PyUnresolvedReferences,PyProtectedMember
from sklearn.impute import IterativeImputer, SimpleImputer

from handler.utils import (
    get_del_col, PTID_COL, NOMINAL_COL_TYPE, NUMERIC_COL_TYPE, normalize, PHENOTYPES_PATH, PHENOTYPES_COL_TYPES_PATH,
    get_cols_by_type
)


def phenotypes_handler(cohort: str):
    """Main method of this module"""

    # Load in the raw data set and the table that indicates the data type of each column
    data_path: str = 'raw-data/{}/phenotypes.csv'.format(cohort)
    data_set: DataFrame = read_csv(data_path, low_memory=False)
    col_types_path: str = PHENOTYPES_COL_TYPES_PATH.format(cohort)
    col_types: DataFrame = read_csv(col_types_path, low_memory=False)

    data_set, col_types = get_mappings(data_set=data_set, col_types=col_types, cohort=cohort)

    # Extract the patient ID column as it cannot be used in the processing
    ptid_col: DataFrame = get_del_col(data_set=data_set, col_types=col_types, col_name=PTID_COL)

    # Process the nominal columns
    nominal_data, nominal_cols = clean_nominal_data(data_set=data_set, data_types=col_types)

    # Process the numeric columns
    numeric_data: DataFrame = clean_numeric_data(
        data_set=data_set, data_types=col_types, nominal_data=nominal_data, nominal_cols=nominal_cols
    )

    # Combine the processed nominal data with the processed numeric data
    data_set: DataFrame = concat([numeric_data, nominal_data], axis=1)

    # Finally add the patient ID column back on so the phenotype data can be joined with other data
    data_set: DataFrame = concat([ptid_col, data_set], axis=1)

    phenotypes_path: str = PHENOTYPES_PATH.format(cohort)
    data_set.to_csv(phenotypes_path, index=False)


def get_mappings(data_set: DataFrame, col_types: DataFrame, cohort: str):
    """Creates mappings from patient ID to other pertinent features, removing rows that don't have them from the data"""

    # TODO: make this work for ANM too

    cdr_feat: str = 'CDGLOBAL'
    feats_to_map: list = [cdr_feat, 'PTGENDER', 'AGE', 'COLPROT']

    for feat in feats_to_map:
        # Remove rows in which the current feature is unknown
        data_set: DataFrame = data_set[data_set[feat].notna()].reset_index()
        del data_set['index']

    # Remove columns that became entirely NA after the above operations
    data_set: DataFrame = data_set.dropna(axis=1, how='all')
    remaining_feats: list = list(data_set)
    remaining_feats.remove(PTID_COL)
    col_types: DataFrame = col_types[remaining_feats].copy()

    # Create a mapping of patient IDs to the current feature
    ptid_col: Series = data_set[PTID_COL].copy()
    ptid_to_feat: dict = {}

    for feat in feats_to_map:
        feat_col: Series = data_set[feat].copy()

        if feat == cdr_feat:
            # Combine the highest CDR category with the second highest category
            max_cat: float = feat_col.max()
            feat_col[feat_col == max_cat] = max_cat - 1

        for ptid, val in zip(ptid_col, feat_col):
            ptid_to_feat[ptid] = val

        ptid_to_feat_path: str = 'clean-data/{}/feat-maps/{}.p'.format(cohort, feat.lower())

        with open(ptid_to_feat_path, 'wb') as f:
            dump(ptid_to_feat, f)

    return data_set, col_types


def clean_nominal_data(data_set: DataFrame, data_types: DataFrame):
    """Processes the nominal data"""

    nominal_data, nominal_cols = get_cols_by_type(data_set=data_set, data_types=data_types, col_type=NOMINAL_COL_TYPE)

    # Impute unknown nominal values
    imputer: SimpleImputer = SimpleImputer(strategy='most_frequent', verbose=2)
    # noinspection PyUnresolvedReferences
    nominal_data: ndarray = nominal_data.to_numpy()
    nominal_data: ndarray = imputer.fit_transform(nominal_data)
    nominal_data: DataFrame = DataFrame(nominal_data, columns=nominal_cols)

    # Ordinal encode each column to save space
    for col_name in nominal_cols:
        col: Series = nominal_data[col_name]
        col, _ = factorize(col)
        del nominal_data[col_name]
        nominal_data.insert(loc=0, column=col_name, value=col)

    return nominal_data, nominal_cols


def clean_numeric_data(
        data_set: DataFrame, data_types: DataFrame, nominal_data: DataFrame, nominal_cols: list, impute_seed=0,
        max_iter=50, n_nearest_features=150
) -> DataFrame:
    """Processes the numeric data"""

    # One hot encode the nominal values for the purpose of imputing unknown real values with a more sophisticated method
    one_hot_nominal_data: DataFrame = get_dummies(nominal_data, columns=nominal_cols, dummy_na=False)

    # Get the numeric columns and column names
    numeric_data, numeric_cols = get_cols_by_type(data_set=data_set, data_types=data_types, col_type=NUMERIC_COL_TYPE)

    # Normalize the numeric columns
    numeric_data: DataFrame = normalize(df=numeric_data)

    n_numeric_cols: int = numeric_data.shape[1]

    # Combine the nominal columns with the numeric so the nominal columns can be used in the imputation
    data_to_impute: ndarray = concatenate([numeric_data.to_numpy(), one_hot_nominal_data.to_numpy()], axis=1)

    # Impute missing numeric values
    imputer: IterativeImputer = IterativeImputer(
        verbose=2, random_state=impute_seed, max_iter=max_iter, max_value=nanmax(data_to_impute),
        min_value=nanmin(data_to_impute), n_nearest_features=n_nearest_features
    )
    imputed_data: ndarray = imputer.fit_transform(data_to_impute)
    assert not isnan(imputed_data.mean())

    # Separate the imputed numeric columns from the nominal columns that helped impute
    numeric_data: ndarray = imputed_data[:, :n_numeric_cols]

    numeric_data: DataFrame = DataFrame(data=numeric_data, columns=numeric_cols)
    return numeric_data
