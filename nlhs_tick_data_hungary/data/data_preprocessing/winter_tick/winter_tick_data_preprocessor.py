import json

import pandas as pd

from nlhs_tick_data_hungary import long_list_path


class WinterTickDataPreprocessor:
    def __init__(self, data: pd.DataFrame):
        self.data = data

        self.result = None

        with open(long_list_path + f'/long_lists.json', 'r+') as file:
            self.groups = json.load(file)

    def run(self) -> None:
        self.adjust_df()
        self.divide_df_to_groups()

    def adjust_df(self) -> None:
        self.data['Bacteria'] = self.data['18×173']
        self.data = self.data.drop(columns=['18×173'])
        self.data = self.data.set_index('Bacteria')

        # Renaming the columns for easier manageability
        cols = list(self.data.T.columns)
        cols[0] = 'Year'
        cols[1] = 'Month'
        cols[2] = 'Gender'

        temp_df = self.data.T
        temp_df.columns = cols
        temp_df.set_index(keys=['Year', 'Month', 'Gender'], inplace=True)
        # TODO: kommentekben leírni, hogy pontosan mi történik
        self.data = temp_df.T

    def divide_df_to_groups(self) -> None:
        self.result = {
            'every_bacteria': self.data,
            'removed_catch_all': self.data[~self.data.index.astype(str).str.contains('atch-all')],
        }

        # TODO: átnevezni a long_lists fájlt -> frissíteni az __init__.py-t (és az implementációs diagramot)
        for group in self.groups:
            self.result[group] = self.data.loc[self.data.index.isin(self.groups[group])]
