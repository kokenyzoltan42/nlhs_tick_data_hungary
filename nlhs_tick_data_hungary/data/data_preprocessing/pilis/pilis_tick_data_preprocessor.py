from typing import Tuple

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.data.data_preprocessing.pilis.column_transformer import ColumnTransformer
from nlhs_tick_data_hungary.data.data_preprocessing.pilis.index_transformer import IndexTransformer


class PilisTickDataPreprocessor:
    def __init__(self, raw_pilis_tick_data: pd.DataFrame):
        self.raw_data = raw_pilis_tick_data

        self.result = None

    def run(self) -> None:
        col_transformer = ColumnTransformer(data=self.raw_data)
        col_transformer.run()

        transformed_cols = self.fill_missing_data(df=col_transformer.data)

        idx_transformer = IndexTransformer(data=transformed_cols)
        temp_regular_data, temp_monthly_data = idx_transformer.run()

        self.result = {
            'regular_data': self.sum_species(temp_regular_data),
            'monthly_data': self.sum_species(temp_monthly_data)
        }

    @staticmethod
    def fill_missing_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fills missing values in the DataFrame with appropriate defaults or previous values.

        This function ensures that the 'Gyűjtők száma' column is filled with data from
        the 'Eredeti csövek száma' column where applicable.
        """
        # Columns where a missing value doesn't mean 0
        remain_nans = ['Eredeti csövek száma', 'Válogatott csövek száma', 'Gyűjtés időtartama (h)',
                       'Egyéb megjegyzés']

        df = df.fillna(np.nan)  # Fill with NaN for clarity
        df['Gyűjtők száma'] = df['Gyűjtők száma'].fillna(df['Eredeti csövek száma'])
        for col in df.columns:
            if col not in remain_nans:
                df[col] = df[col].fillna(0)

        return df

    @staticmethod
    def sum_species(df: pd.DataFrame) -> pd.DataFrame:
        # Renaming columns columns for easier manageability
        df = df.rename(columns={
            'H. lárva': 'H. concinna lárva',
            'I. lárva': 'I. ricinus lárva'
        })

        # Creating a summary table for every species
        species_groups = {}
        for col in df.columns:
            # Identifying the species
            species_name = " ".join(col.split()[:2])
            if species_name not in species_groups:
                species_groups[species_name] = []
            species_groups[species_name].append(col)

        # Summing the columns for every species
        for species, columns in species_groups.items():
            df[species] = df[columns].sum(axis=1)

        # Creating new columns for tha adult stages
        df['I. ricinus adult'] = df['I. ricinus hím'] + df['I. ricinus nőstény']
        df['H. inermis adult'] = df['H. inermis hím'] + df['H. inermis nőstény']
        df['H. concinna adult'] = df['H. concinna hím'] + df['H. concinna nőstény']
        df['D. marginatus adult'] = df['D. marginatus hím'] + df['D. marginatus nőstény']
        df['D. reticulatus adult'] = df['D. reticulatus hím'] + df['D. reticulatus nőstény']

        return df
