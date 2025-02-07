import json

import pandas as pd

from nlhs_tick_data_hungary import config_path


class WinterTickDataPreprocessor:
    """
    This class is responsible for preprocessing winter tick data. It adjusts the dataframe structure, prepares it
    for further analysis, and divides it into different groups based on predefined categories.

    data (pd.DataFrame): The raw data to be processed.
    result (dict): The final processed data organized into different groups.
    groups (dict): The predefined groups (loaded from a `.json` file).
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initializes the WinterTickDataPreprocessor with the provided data.

        :param data: The raw data to be preprocessed.
        """
        self.data = data
        self.result = None

        # Load the predefined group configurations from a `.json` file
        with open(config_path + f'/groups.json', 'r+') as file:
            self.groups = json.load(file)

    def run(self) -> None:
        """
        Runs the preprocessing pipeline:
        - Adjust the dataframe to a multi-index-like structure.
        - Divide the data into groups as specified in the configuration file.
        """
        self.adjust_df()
        self.divide_df_to_groups()

    def adjust_df(self) -> None:
        """
        Adjusts the dataframe to a format where:
        - The rows are indexed by 'Bacteria'.
        - The columns are reorganized to represent 'Year', 'Month', and 'Gender'.
        - After transposing and reindexing, the structure will resemble a multi-index
          format with 'Year', 'Month', and 'Gender' as the hierarchical levels.

        The result is in a multi-index-like dataframe. For example, to get data for '2022 October Female 1',
        the access would look like: df['2022']['October']['Female 1'].
        """
        # Renaming '18×173' column to 'Bacteria' and drop the old column
        self.data['Bacteria'] = self.data['18×173']
        self.data = self.data.drop(columns=['18×173'])

        # Setting 'Bacteria' as the index of the dataframe
        self.data = self.data.set_index('Bacteria')

        # Transposing the dataframe so that the columns become rows
        cols = list(self.data.T.columns)

        # Renaming the columns to 'Year', 'Month', and 'Gender'
        cols[0] = 'Year'
        cols[1] = 'Month'
        cols[2] = 'Gender'

        # Temporary dataframe to hold the transposed data
        temp_df = self.data.T
        temp_df.columns = cols

        # Setting 'Year', 'Month', and 'Gender' as the multi-index
        temp_df.set_index(keys=['Year', 'Month', 'Gender'], inplace=True)

        # Transposing the dataframe back to restore the original structure
        self.data = temp_df.T

    def divide_df_to_groups(self) -> None:
        """
        Divides the dataframe into multiple groups based on the predefined categories
        loaded from the 'groups.json' file. Each group will be a subset
        of the data, and the result will be stored in the `self.result` attribute.

        - THe group called 'every_bacteria' that contains all data.
        - THe group called 'removed_catch_all' that excludes rows with 'catch-all' in their index.
        - Additional groups for each predefined category in the 'groups.json' file
        ('1.csoport', '2.csoport', '3.csoport').

        """
        self.result = {
            'every_bacteria': self.data,
            # Exclude rows with 'catch-all' in the index
            # There is an instance where 'catch-all' is with a capital C ('Rickettsia Catch-all (23-5s rRNA)')
            'removed_catch_all': self.data[~self.data.index.astype(str).str.contains('atch-all')],
        }

        for group in self.groups:
            self.result[group] = self.data.loc[self.data.index.isin(self.groups[group])]
