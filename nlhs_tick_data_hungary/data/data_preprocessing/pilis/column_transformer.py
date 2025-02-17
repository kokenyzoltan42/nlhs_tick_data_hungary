import json

import pandas as pd
import re

from nlhs_tick_data_hungary import config_path


class ColumnTransformer:
    """
    A class for transforming columns in a DataFrame.

    This class is responsible for renaming columns, adjusting data types, and splitting temperature and
    relative humidity (RH) columns into separate minimum and maximum values.

    data (pd.DataFrame): The DataFrame that will be processed.
    long_lists (dict): A dictionary containing predefined long lists of tick species and stages.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initializes the ColumnTransformer with the given DataFrame and loads the necessary configurations.

        :param data: A pandas DataFrame containing the raw data to be transformed.
        """
        self.data = data

        # Load predefined lists from the 'long_lists.json'
        with open(config_path + f'/long_lists.json', 'r+') as file:
            self.long_lists = json.load(file)

    def run(self) -> None:
        """
        Runs the full transformation pipeline on the DataFrame.

        This method (sequentially) applies renaming, column adjustments, and splits temperature and RH columns
        into min and max values.
        """
        self.rename_unnamed_columns()
        self.adjust_columns()
        self.split_temps_and_rhs()

    def rename_unnamed_columns(self) -> None:
        """
        Renames unnamed columns and other columns based on the predefined long lists.

        The column "Unnamed: 7" is renamed to "RH(%)", and other columns  related to tick species and stages are
        renamed accordingly based on the 'tick_species_and_stages' list in the configuration.
        After renaming, the first row is dropped and the index is reset.

        The renaming is necessary because during the load of the data many column names go missing, because in the
        original Google Spreadsheet for example the tick stages' names are in the second row.
        """
        # Most of the wrongly loaded column names (except "RH(%)") are after the column named "Összes kullancs (db)"
        self.data = self.data.rename(columns={"Unnamed: 7": "RH(%)"})
        # Find the index of the column 'Összes kullancs (db)' and create a dictionary for renaming
        kullancs_index = self.data.columns.get_loc("Összes kullancs (db)") + 1
        rename_dict = {self.data.columns[i]: self.long_lists["tick_species_and_stages"][i - kullancs_index] for i in
                       range(kullancs_index, len(self.data.columns))}

        # Rename the columns based on the created dictionary
        self.data = self.data.rename(columns=rename_dict)

        # Drop the first row and reset the index
        self.data = self.data.drop(index=0).reset_index().drop(columns="index")

    def adjust_columns(self) -> None:
        """
        Adjusts the columns of the DataFrame, specifically converting certain columns to float.

        The columns listed in 'tick_species_and_stages' as well as some additional columns are converted to float.
        The 'Gyűjtés időtartama (h)' column is also converted, replacing commas with dots to identify floating numbers.
        """
        # Define the columns that need to be converted to float
        columns_to_float = self.long_lists["tick_species_and_stages"] + ['Gyűjtők száma', 'Összes kullancs (db)']

        # Convert the specified columns to float type
        self.data[columns_to_float] = self.data[columns_to_float].astype(float)

        # Convert the 'Gyűjtés időtartama (h)' column by replacing commas with dots and then converting to float
        self.data["Gyűjtés időtartama (h)"] = self.data["Gyűjtés időtartama (h)"].str.replace(',', '.').astype(float)

    @staticmethod
    def split_min_max(temp: pd.Series) -> pd.Series:
        """
        Splits a series containing temperature or RH values into minimum and maximum values.

        If a value is a single number, both min and max will be set to that number. If it's an interval
        (e.g., "10-20"), it splits it into min and max.

        :param temp: A pandas Series containing temperature or RH values to be split.
        :return: A pandas Series containing minimum and maximum values.
        """
        temp = str(temp).replace(',', '.').strip()
        if re.match(pattern=r"^\s*\d+([.,]\d+)?\s*$", string=temp):
            # If there is only one number
            min_val = max_val = float(temp)
            return pd.Series([min_val, max_val])
        elif re.match(pattern=r"^\s*\d+([.,]\d+)?\s*-\s*\d+([.,]\d+)?\s*$", string=temp):
            # If there is an interval
            min_val, max_val = map(float, temp.split('-'))
            return pd.Series([min_val, max_val])
        else:
            return pd.Series([None, None])  # Return None if the format is invalid

    def split_temps_and_rhs(self) -> None:
        """
        Splits the 'T (°C)' and 'RH(%)' columns into separate minimum and maximum columns.

        This function calls the split_min_max method to process each respective column
        and then drops the original columns after extraction.
        """
        self.data[['Min - T (°C)', 'Max - T (°C)']] = self.data['T (°C)'].apply(self.split_min_max)
        self.data[['Min - RH(%)', 'Max - RH(%)']] = self.data['RH(%)'].apply(self.split_min_max)

        # Drop the original columns
        self.data.drop(columns=['T (°C)', 'RH(%)'], inplace=True)
