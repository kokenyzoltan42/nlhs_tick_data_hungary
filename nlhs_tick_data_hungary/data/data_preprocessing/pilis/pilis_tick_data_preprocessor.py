import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.data.data_preprocessing.pilis.column_transformer import ColumnTransformer
from nlhs_tick_data_hungary.data.data_preprocessing.pilis.index_transformer import IndexTransformer


class PilisTickDataPreprocessor:
    """
    A class for preprocessing raw tick data from the Pilis region.

    The class handles the following steps:
    - Column transformations, such as renaming and filling missing values.
    - Index transformations, which adjust the indices based on date.
    - Aggregation of tick species data, including summing counts for each species and stages.

    raw_data (pd.DataFrame): The raw tick data provided for preprocessing.
    result (dict): A dictionary containing the transformed data, including both regular and monthly summaries.
    """

    def __init__(self, raw_pilis_tick_data: pd.DataFrame):
        """
        Initializes the preprocessor with raw tick data.

        :param raw_pilis_tick_data: A pandas DataFrame containing the raw tick data for preprocessing.
        """
        self.raw_data = raw_pilis_tick_data
        self.result = None

    def run(self) -> None:
        """
        Runs the preprocessing pipeline.

        This method performs column transformations, fills missing data, and transforms the indices.
        It then aggregates the tick species data into regular and monthly summaries.

        The final result is stored in the `result` attribute as a dictionary with two entries:
        - 'regular_data': A DataFrame containing the transformed data with regular indices.
        - 'monthly_data': A DataFrame containing the transformed data with monthly period indices.
        """
        # Apply column transformations
        col_transformer = ColumnTransformer(data=self.raw_data)
        col_transformer.run()

        # Fill missing data in the columns
        transformed_cols = self.fill_missing_data(df=col_transformer.data)

        # Apply index transformations (regular and monthly)
        idx_transformer = IndexTransformer(data=transformed_cols)
        temp_regular_data, temp_monthly_data = idx_transformer.run()

        # Aggregate species data and store the result
        self.result = {
            'regular_data': self.sum_species(temp_regular_data),
            'monthly_data': self.sum_species(temp_monthly_data)
        }

    @staticmethod
    def fill_missing_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fills missing values in the DataFrame with appropriate defaults or previous values.

        - The 'Gyűjtők száma' column's missing values are filled using the values in 'Eredeti csövek száma'.
        - Other columns are filled with 0, except for specific columns that allow NaN values.

        :param df: The DataFrame containing the data with missing values.
        :return: The DataFrame with missing values filled.
        """
        # List of columns where NaN values should remain (i.e., not filled with 0)
        remain_nans = ['Eredeti csövek száma', 'Válogatott csövek száma', 'Gyűjtés időtartama (h)',
                       'Egyéb megjegyzés']

        # Fill all NaN values with np.nan for clarity
        df = df.fillna(np.nan)

        # Fill 'Gyűjtők száma' with values from 'Eredeti csövek száma'
        df['Gyűjtők száma'] = df['Gyűjtők száma'].fillna(df['Eredeti csövek száma'])

        # Fill other columns with 0, except those in the remain_nans list
        for col in df.columns:
            if col not in remain_nans:
                df[col] = df[col].fillna(0)

        return df

    @staticmethod
    def sum_species(df: pd.DataFrame) -> pd.DataFrame:
        """
        Sums tick counts for each species, aggregating the data by species and life stage.

        The method also creates new columns for the adult stages by summing the male and female counts
        for each species. The resulting DataFrame includes summed species data for both larvae and adults.

        :param df: The DataFrame containing tick species data with individual life stages.
        :return: The DataFrame with summed species data for larvae and adults.
        """
        # Renaming specific columns for easier management
        df = df.rename(columns={
            'H. lárva': 'H. concinna lárva',
            'I. lárva': 'I. ricinus lárva'
        })

        # Create a dictionary to group columns by species
        species_groups = {}
        for col in df.columns:
            # Identify the species name (first two words in the column name)
            species_name = " ".join(col.split()[:2])
            if species_name not in species_groups:
                species_groups[species_name] = []
            species_groups[species_name].append(col)

        # Sum the columns for each species
        for species, columns in species_groups.items():
            df[species] = df[columns].sum(axis=1)

        # Add new columns for adult stages by summing male and female counts
        df['I. ricinus adult'] = df['I. ricinus hím'] + df['I. ricinus nőstény']
        df['H. inermis adult'] = df['H. inermis hím'] + df['H. inermis nőstény']
        df['H. concinna adult'] = df['H. concinna hím'] + df['H. concinna nőstény']
        df['D. marginatus adult'] = df['D. marginatus hím'] + df['D. marginatus nőstény']
        df['D. reticulatus adult'] = df['D. reticulatus hím'] + df['D. reticulatus nőstény']

        return df
