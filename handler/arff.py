"""Processes the data and converts it to an ARFF file"""

from pandas import concat, DataFrame, get_dummies, factorize, read_csv, Series, merge
from os.path import join
from numpy import concatenate, ndarray, nanmin, nanmax, isnan
# noinspection PyUnresolvedReferences
from sklearn.experimental import enable_iterative_imputer
# noinspection PyUnresolvedReferences,PyProtectedMember
from sklearn.impute import IterativeImputer, SimpleImputer

from handler.utils import ARFF_PATH, PTID_COL, PTID_CSV, get_del_col

NUMERIC_COL_TYPE: str = 'numeric'
NOMINAL_COL_TYPE: str = 'nominal'


def arff_handler(cohort: str, target_col: str):
    """Main function of this module"""

    # Get the raw data directory for the given cohort
    raw_data_dir: str = 'raw-data'
    raw_data_dir: str = join(raw_data_dir, cohort)

    # TODO: Load in MRI data too
    # mri_data, mri_col_types, n_mri_cols = process_numeric_data(
    #     raw_data_dir=raw_data_dir, csv='mri.csv'
    # )

    # Handle the expression data
    expression_data, expression_col_types, n_expression_cols = process_numeric_data(
        raw_data_dir=raw_data_dir, csv='expression.csv'
    )

    # Handle the phenotype data
    phenotype_data, phenotype_col_types = process_phenotype_data(raw_data_dir=raw_data_dir, target_col=target_col)
    n_phenotype_cols: int = phenotype_data.shape[-1] - 1

    # Merge the data sets by PTID and then remove the PTID column, which is only used to merge
    combined_data: DataFrame = merge(expression_data, phenotype_data, on=PTID_COL, how='inner')
    ptid_col: DataFrame = combined_data[[PTID_COL]].copy()
    del combined_data[PTID_COL]

    # Save the patient ID column for later
    ptid_col.to_csv(PTID_CSV.format(cohort), index=False)

    assert combined_data.shape[-1] == n_expression_cols + n_phenotype_cols
    col_types: DataFrame = concat([expression_col_types, phenotype_col_types], axis=1)

    # Convert the data to ARFF format and save it as an ARFF file
    save_data(arff_data=combined_data, col_types=col_types, target_col=target_col, cohort=cohort)


def process_numeric_data(raw_data_dir: str, csv: str):
    """Processes a data set that is complete, needs no targets, and entirely numeric"""

    data: DataFrame = read_csv(join(raw_data_dir, csv), low_memory=False)
    ptid_col: DataFrame = get_del_col(data_set=data, col_types=None, col_name=PTID_COL)
    data: DataFrame = normalize(df=data)
    n_cols: int = data.shape[-1]
    col_types: list = [NUMERIC_COL_TYPE] * n_cols
    col_types: DataFrame = DataFrame(data=[col_types], columns=list(data))
    data: DataFrame = concat([ptid_col, data], axis=1)
    return data, col_types, n_cols


def process_phenotype_data(raw_data_dir: str, target_col: str) -> tuple:
    """Cleans up the phenotype data according to its specific needs"""

    # Load in the raw data set and the table that indicates the data type of each column
    data_path: str = join(raw_data_dir, 'phenotypes.csv')
    data_set: DataFrame = read_csv(data_path, low_memory=False)
    col_types_path: str = join(raw_data_dir, 'phenotype-col-types.csv')
    col_types: DataFrame = read_csv(col_types_path, low_memory=False)

    # Remove rows with unknown targets
    if target_col is not None:
        data_set: DataFrame = data_set[data_set[target_col].notna()].reset_index()
        del data_set['index']

    # Remove columns that are entirely NA
    data_set: DataFrame = data_set.dropna(axis=1, how='all')

    # Extract the patient ID column as it cannot be used in the processing
    ptid_col: DataFrame = get_del_col(data_set=data_set, col_types=col_types, col_name=PTID_COL)

    col_types: DataFrame = col_types[list(data_set)]
    targets = None

    if target_col is not None:
        # Separate the targets
        targets: Series = get_del_col(data_set=data_set, col_types=col_types, col_name=target_col)[target_col]

        # Combine the highest target category with the second highest category
        max_cat: float = targets.max()
        targets[targets == max_cat] = max_cat - 1

        # Ordinal encode the targets
        targets, _ = factorize(targets)

        targets: DataFrame = DataFrame(targets, columns=[target_col])

    # Process the nominal columns
    nominal_data, nominal_cols = clean_nominal_data(data_set=data_set, data_types=col_types)

    # Process the numeric columns
    numeric_data: DataFrame = clean_numeric_data(
        data_set=data_set, data_types=col_types, nominal_data=nominal_data, nominal_cols=nominal_cols, targets=targets
    )

    # Combine the processed nominal data with the processed numeric data and the targets if applicable
    if targets is not None:
        data_set: DataFrame = concat([numeric_data, nominal_data, targets], axis=1)
    else:
        data_set: DataFrame = concat([numeric_data, nominal_data], axis=1)

    # Finally add the patient ID column back on so the phenotype data can be joined with other data
    data_set: DataFrame = concat([ptid_col, data_set], axis=1)

    return data_set, col_types


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
    data_set: DataFrame, data_types: DataFrame, nominal_data: DataFrame, nominal_cols: list, targets: DataFrame,
    impute_seed=0, max_iter=10, n_nearest_features=100
) -> DataFrame:
    """Processes the numeric data"""

    # One hot encode the nominal values for the purpose of imputing unknown real values with a more sophisticated method
    one_hot_nominal_data: DataFrame = get_dummies(nominal_data, columns=nominal_cols, dummy_na=False)

    if targets is not None:
        one_hot_targets: DataFrame = get_dummies(targets, columns=list(targets), dummy_na=False)
    else:
        one_hot_targets = None

    # Get the numeric columns and column names
    numeric_data, numeric_cols = get_cols_by_type(data_set=data_set, data_types=data_types, col_type=NUMERIC_COL_TYPE)

    # Normalize the numeric columns
    numeric_data: DataFrame = normalize(df=numeric_data)

    n_numeric_cols: int = numeric_data.shape[1]

    # Combine the nominal columns with the numeric so the nominal columns can be used in the imputation
    if one_hot_targets is not None:
        data_to_impute: ndarray = concatenate(
            [numeric_data.to_numpy(), one_hot_nominal_data.to_numpy(), one_hot_targets.to_numpy()], axis=1
        )
    else:
        data_to_impute: ndarray = concatenate(
            [numeric_data.to_numpy(), one_hot_nominal_data.to_numpy()], axis=1
        )

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


def save_data(arff_data: DataFrame, col_types: DataFrame, target_col: str, cohort: str):
    """Stores the data on disk as an ARFF and a CSV"""

    arff_name: str = ARFF_PATH.format(cohort)

    # Save the data of the ARFF as a CSV so the header can be added to it
    arff_data.to_csv(arff_name, index=False)

    # Open the ARFF as a text file to edit
    with open(arff_name, 'r') as f:
        arff: str = f.read()

    # Remove the first line
    arff: list = arff.split('\n')
    arff: list = arff[1:]

    # Remove empty strings
    while '' in arff:
        arff.remove('')

    # Make the header
    header: list = ['@RELATION {}'.format(cohort.upper())]

    col_names: list = list(arff_data)
    for col_name in col_names:
        line: str = '@ATTRIBUTE {}'.format(col_name)

        if col_name == target_col:
            is_numeric: bool = False
        else:
            is_numeric: bool = col_types.loc[0, col_name] == NUMERIC_COL_TYPE

        if is_numeric:
            line += ' ' + 'NUMERIC'
        else:
            col: Series = arff_data[col_name]
            categories: set = set(col.unique())
            line += ' ' + str(categories).replace(' ', '')

        header.append(line)

    header.append('@DATA')

    # Attach the header to the ARFF
    header.extend(arff)
    arff: list = header

    # Rewrite the ARFF with the header included
    with open(arff_name, 'w') as f:
        for line in arff:
            f.write(line + '\n')
