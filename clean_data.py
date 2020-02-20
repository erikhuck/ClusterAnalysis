from pandas import read_csv
from pandas import DataFrame
from pandas import Series


def clean_data(data_path: str, data_types_path: str):
    data_set: DataFrame = read_csv(data_path)
    data_types: DataFrame = read_csv(data_types_path)
    
    col_names: list = list(data_types)

    for col_name in col_names:
        col: Series = data_set[col_name]
        pass
