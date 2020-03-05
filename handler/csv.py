"""Takes the features selected by WEKA to create a CSV data set for deep learning"""

from numpy import array, ndarray
from pandas import concat, DataFrame, get_dummies


def get_col_to_type(arff: list) -> dict:
    """Makes a mapping of column name to column data type where numeric is True and nominal is False"""

    data_idx: int = arff.index('@DATA')
    cols: list = arff[1:data_idx]
    col_to_type: dict = {}
    for item in cols:
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


def get_data_set(data: DataFrame, col_to_type: dict, kept_feats: list) -> DataFrame:
    """Creates the final data set from the selected features and one-hot encoded nominal columns"""

    # Splice out the targets
    target_col: str = 'CDCOMMUN'
    targets: DataFrame = data[[target_col]].copy()
    
    # Splice out only the selected features
    data: DataFrame = data[kept_feats].copy()

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

    # Combine the numeric, nominal, and target columns into one complete data set
    data: DataFrame = concat([numeric_data, nominal_data, targets], axis=1)

    return data


def csv_handler(arff_path: str, kept_feats: str):
    """Main function of this module"""

    # Open the ARFF file to get the data, columns, and column types
    with open(arff_path, 'r') as f:
        arff: str = f.read()
    arff: list = arff.split('\n')
    arff.remove('')
    assert '' not in arff

    # Make a dictionary of column name to column type
    col_to_type: dict = get_col_to_type(arff=arff)

    # Make the initial data frame
    data: DataFrame = get_data(arff=arff, col_names=list(col_to_type.keys()))
    
    # Load in the columns that were selected by a feature selection algorithm
    with open(kept_feats, 'r') as f:
        kept_feats: str = f.read()
    kept_feats: list = kept_feats.split('\n')
    kept_feats.remove('')
    assert '' not in kept_feats

    # Construct the final data set using only the selected features
    data: DataFrame = get_data_set(data=data, col_to_type=col_to_type, kept_feats=kept_feats)

    # Save the CSV
    data.to_csv('data.csv', index=False)
