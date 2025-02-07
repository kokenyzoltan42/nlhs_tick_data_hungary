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

        # self.data = self.data.rename(columns={
        #    "Unnamed: 7": "RH(%)",
        #    "Kullancs mennyiség/faj (db)": "I. ricinus nőstény",
        #    "Unnamed: 11": "I. ricinus hím",
        #    "Unnamed: 12": "I. ricinus nimfa",
        #    "Unnamed: 13": "I. lárva",
        #    "Unnamed: 14": "H. inermis nőstény",
        #    "Unnamed: 15": "H. inermis hím",
        #    "Unnamed: 16": "H. inermis nimfa",
        #    "Unnamed: 17": "H. concinna nőstény",
        #    "Unnamed: 18": "H. concinna hím",
        #    "Unnamed: 19": "H. concinna nimfa",
        #    "Unnamed: 20": "H. lárva",
        #    "Unnamed: 21": "D. marginatus nőstény",
        #    "Unnamed: 22": "D. marginatus hím",
        #    "Unnamed: 23": "D. marginatus nimfa",
        #    "Unnamed: 24": "D. marginatus lárva",
        #    "Unnamed: 25": "D. reticulatus nőstény",
        #    "Unnamed: 26": "D. reticulatus hím",
        #    "Unnamed: 27": "D. reticulatus nimfa",
        #    "Unnamed: 28": "D. reticulatus lárva",
        # })

        # TODO: LEELLENŐRIZNI!!!

        self.data = self.data.rename(columns={"Unnamed: 7": "RH(%)"})

        kullancs_index = self.data.columns.get_loc("Összes kullancs (db)") + 1
        rename_dict = {self.data.columns[i]: self.long_lists["tick_species_and_stages"][i - kullancs_index] for i in
                       range(kullancs_index, len(self.data.columns))}

        self.data.rename(columns=rename_dict)
        # Drop the first row and reset the index
        self.data = self.data.drop(index=0).reset_index().drop(columns="index")

    def adjust_columns(self) -> None:
        print(self.data.columns)
        print("Long_list:", self.long_lists["tick_species_and_stages"])

        # Defining columns that need to be converted to float
        columns_to_float = self.long_lists["tick_species_and_stages"] + ['Gyűjtők száma', 'Összes kullancs (db)']
        print("Columns_to_float:", columns_to_float)

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
