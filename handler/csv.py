"""Takes the features selected by WEKA to create a CSV data set for deep learning"""

from numpy import array, ndarray
from pandas import concat, DataFrame, get_dummies, read_csv

from handler.utils import PTID_CSV, ARFF_PATH, CSV_PATH


def get_col_to_type(arff: list) -> dict:
    """Makes a mapping of column name to column data type where numeric is True and nominal is False"""

    data_idx: int = arff.index('@DATA')
    cols: list = arff[1:data_idx]
    col_to_type: dict = {}

    for item in cols:
        # noinspection PyUnresolvedReferences
        item: list = item.split(' ')
        assert '' not in item
        col_name: str = item[1]

        # Let numeric be True and nominal be False
        col_type: bool = item[-1] == 'NUMERIC'
        col_to_type[col_name] = col_type

    return col_to_type


def get_data(arff: list, col_names: list) -> DataFrame:
    """Makes a data frame from ARFF data and column names"""

    data_idx: int = arff.index('@DATA') + 1
    data: list = arff[data_idx:]

    for i, instance in enumerate(data):
        # noinspection PyUnresolvedReferences
        instance: list = instance.split(',')
        assert '' not in instance
        assert len(instance) == len(col_names)

        for j, val in enumerate(instance):
            instance[j] = float(val)

        data[i] = instance

    data: ndarray = array(data)
    data: DataFrame = DataFrame(data, columns=col_names)

    return data


def get_data_set(data: DataFrame, col_to_type: dict, target_col: str, kept_feats: str, cohort: str) -> DataFrame:
    """Creates the final data set from the selected features and one-hot encoded nominal columns"""

    targets = None

    if target_col is not None:
        # Splice out the targets
        targets: DataFrame = data[[target_col]].copy()

    if kept_feats is not None:
        # Load in the columns that were selected by a feature selection algorithm
        with open(kept_feats, 'r') as f:
            kept_feats: str = f.read()

        kept_feats: list = kept_feats.split('\n')
        kept_feats.remove('')
        assert '' not in kept_feats

        # Splice out only the selected features
        data: DataFrame = data[kept_feats].copy()
    elif target_col is not None:
        # Since features are not being selected, we must temporarily remove the target column
        del data[target_col]

    # Separate the nominal features from the numeric features
    nominal_cols: list = []
    numeric_cols: list = []

    for col in list(data):
        if col_to_type[col]:
            numeric_cols.append(col)
        else:
            nominal_cols.append(col)

    # Splice out the nominal columns
    nominal_data: DataFrame = data[nominal_cols].copy()

    # One-hot encode the nominal data
    nominal_data: DataFrame = get_dummies(nominal_data, columns=nominal_cols, dummy_na=False)
    
    # Splice out the numeric columns
    numeric_data: DataFrame = data[numeric_cols].copy()

    # Combine the numeric, nominal, and target columns (if applicable) into one complete data set
    if targets is not None:
        data: DataFrame = concat([numeric_data, nominal_data, targets], axis=1)
    else:
        data: DataFrame = concat([numeric_data, nominal_data], axis=1)

    # Concatenate the patient ID column
    ptid_col: DataFrame = read_csv(PTID_CSV.format(cohort))
    data: DataFrame = concat([ptid_col, data], axis=1)

    # Shuffle the data set
    data: DataFrame = data.sample(frac=1, axis=0, random_state=0)

    return data


def csv_handler(cohort: str, target_col: str, kept_feats: str):
    """Main function of this module"""

    # Open the ARFF file to get the data, columns, and column types
    arff_path: str = ARFF_PATH.format(cohort)

    with open(arff_path, 'r') as f:
        arff: str = f.read()

    arff: list = arff.split('\n')
    arff.remove('')
    assert '' not in arff

    # Make a dictionary of column name to column type
    col_to_type: dict = get_col_to_type(arff=arff)

    # Make the initial data frame
    data: DataFrame = get_data(arff=arff, col_names=list(col_to_type.keys()))
    
    # Construct the final data set using only the selected features
    data: DataFrame = get_data_set(
        data=data, col_to_type=col_to_type, target_col=target_col, kept_feats=kept_feats, cohort=cohort
    )

    # Save the CSV
    csv_path: str = CSV_PATH.format(cohort)
    data.to_csv(csv_path, index=False)
