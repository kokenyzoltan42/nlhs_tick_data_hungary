import json

import pandas as pd
import re

from nlhs_tick_data_hungary import config_path


class ColumnTransformer:
    def __init__(self, data: pd.DataFrame):
        self.data = data

        with open(config_path + f'/long_lists.json', 'r+') as file:
            self.long_lists = json.load(file)

    def run(self) -> None:
        self.rename_unnamed_columns()
        self.adjust_columns()
        self.split_temps_and_rhs()

    def rename_unnamed_columns(self) -> None:

        self.data = self.data.rename(columns={"Unnamed: 7": "RH(%)"})

        kullancs_index = self.data.columns.get_loc("Összes kullancs (db)") + 1
        rename_dict = {self.data.columns[i]: self.long_lists["tick_species_and_stages"][i - kullancs_index] for i in
                       range(kullancs_index, len(self.data.columns))}

        self.data = self.data.rename(columns=rename_dict)
        # Drop the first row and reset the index
        self.data = self.data.drop(index=0).reset_index().drop(columns="index")

    def adjust_columns(self) -> None:

        # Defining columns that need to be converted to float
        columns_to_float = self.long_lists["tick_species_and_stages"] + ['Gyűjtők száma', 'Összes kullancs (db)']

        # Convert specific columns to float
        self.data[columns_to_float] = self.data[columns_to_float].astype(float)
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
