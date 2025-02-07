import json
from typing import Tuple

import pandas as pd

from nlhs_tick_data_hungary import config_path


class IndexTransformer:
    """
    A class for transforming and adjusting the indices of a DataFrame based on date and collection data.

    This class performs the following operations on the DataFrame:
    - Removes specific rows based on predefined red dates.
    - Transforms collection dates to a proper datetime index.
    - Adjusts the month in the 'Date' column to ensure continuity in month values.
    - Creates two different DataFrame representations:
        - A basic transformation with datetime as the index.
        - A transformation that adjusts the indices to a monthly period format, aggregating data accordingly.

    data (pd.DataFrame): The DataFrame that will be transformed.
    """
    def __init__(self, data: pd.DataFrame):
        """
        Initializes the IndexTransformer with the given DataFrame.

        :param data: A pandas DataFrame containing the raw data to be transformed.
        """
        self.data = data

        with open(config_path + f'/long_lists.json', 'r+') as file:
            long_lists = json.load(file)

        self.red_dates = long_lists['red_dates']

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Runs the transformation pipeline, applying all necessary steps.

        This method will call the following transformations:
        - Remove specific rows based on red dates.
        - Transform the indices to a basic datetime format and monthly period format.

        :return: A tuple containing two DataFrames:
                 - Basic transformed DataFrame with datetime as index.
                 - Monthly transformed DataFrame with period as index.
        """
        self.remove_reds()

        return self.transform_indices_basic(), self.transform_indices_monthly_period()

    # TODO: hozzáadni az implementációs diagramhoz
    @staticmethod
    def adjust_months(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adjusts the 'Date' column in the DataFrame to ensure continuity in month values.

        This function checks consecutive rows for the same month and decrements the previous
        month if a duplication is found.
        For example: We have two dates: '2019.09.16' and '2019.09.27'. They are in the same month therefore, the
        first date in the month ('2019.09.16') should be in August.

        This method doesn't produce duplicates in the rows because the only instance (except the first couple of rows)
        where there are duplicates in the indices is when there wasn't any data recorded in the previous month.

        :param df: The DataFrame containing a 'Date' column.
        :return: The DataFrame with adjusted month values.
        """
        prev_month = None
        for idx, row in df.iterrows():
            # In the first couple of rows this logic fails beacause there are more than two dates in one month
            # Therefore we skip those rows and only manipulate them in the transform_indices_monthly_period method
            if idx > 7:
                if prev_month == row['Date']:  # If the previous row is in the same month
                    # Move the previous row to the previous month
                    df.at[idx - 1, 'Date'] = row['Date'] - pd.DateOffset(months=1)
                prev_month = row['Date']
        return df

    def remove_reds(self) -> None:
        """
        Removes rows with specific dates (marked as red in the Google Spreadsheet).

        The red dates are predefined and listed in the method. Rows with these dates will be removed
        from the DataFrame.
        """
        self.data = self.data[~self.data['Gyűjtési dátum'].isin(self.red_dates)]

        # Reset the index after filtering
        self.data.reset_index(drop=True, inplace=True)

    def transform_indices_basic(self) -> pd.DataFrame:
        """
        Transforms the indices of the DataFrame to a basic datetime format.

        The method converts the 'Gyűjtési dátum' column to a datetime format and sets it as the index,
        dropping the original 'Gyűjtési dátum' column.

        :return: The DataFrame with the transformed datetime index.
        """
        df = self.data.copy()

        df['Date'] = pd.to_datetime(df['Gyűjtési dátum'], format='mixed')

        df = df.drop(columns=['Gyűjtési dátum'])
        df.set_index('Date', inplace=True)

        return df

    def transform_indices_monthly_period(self) -> pd.DataFrame:
        """
        Transforms the indices of the DataFrame to a monthly period format.

        This method converts the 'Gyűjtési dátum' to a period format representing months ('M'),
        groups the data by this monthly period, and performs aggregation on the columns.
        Additionally, it adjusts the months to ensure continuity and reindexes the DataFrame
        to cover the full date range, resampling by month-end.

        :return: The DataFrame with monthly period as index and aggregated data.
        """
        df = self.data.copy()

        # Convert collection dates to periods
        df['Date'] = pd.to_datetime(df['Gyűjtési dátum'], format='mixed').dt.to_period('M')
        df['Date'] = df['Date'].dt.to_timestamp()

        df = df.drop(columns=['Gyűjtési dátum'])

        # Adjusting months (after the first couple of rows)
        df = self.adjust_months(df=df)

        df.set_index('Date', inplace=True)

        # Handling the first couple of rows where there are more the two data for a given month
        df = df.resample('ME').agg({
            'Min - T (°C)': 'mean',
            'Max - T (°C)': 'mean',
            'Min - RH(%)': 'mean',
            'Max - RH(%)': 'mean',
            'Gyűjtés helye': 'first',  # erre szükség van?
            **{col: 'sum' for col in df if col not in ['Date',
                                                       'Min - T (°C)', 'Max - T (°C)', 'Min - RH(%)',
                                                       'Max - RH(%)', 'Gyűjtés helye']}
        }).reset_index()

        df.set_index('Date', inplace=True)
        df.index = df.index.to_period('M')

        return df
