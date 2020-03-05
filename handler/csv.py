"""Takes the features selected by WEKA to create a CSV data set for deep learning"""

# from pandas import concat, DataFrame, get_dummies


def csv_handler(arff_path: str, kept_feats: str):
    """Main function of this module"""

    # For the csv, one-hot encode the nominal data
    # nominal_data: DataFrame = get_dummies(nominal_data, columns=nominal_cols, dummy_na=False)
    # csv_data: DataFrame = concat([numeric_data, nominal_data, targets], axis=1)

    # csv_name: str = 'data.csv'

    # # Save the CSV
    # csv_data.to_csv(csv_name, index=False)
    pass
