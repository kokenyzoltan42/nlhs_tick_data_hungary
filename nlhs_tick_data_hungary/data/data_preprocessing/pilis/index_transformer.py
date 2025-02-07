from typing import Tuple

import pandas as pd


class IndexTransformer:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
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
        red_dates = ['2015-05-13', '2015-06-05', '2015-07-01', '2016-06-22']
        self.data = self.data[~self.data['Gyűjtési dátum'].isin(red_dates)]

        # Reset the index after filtering
        self.data.reset_index(drop=True, inplace=True)

    def transform_indices_basic(self) -> pd.DataFrame:
        df = self.data.copy()

        df['Date'] = pd.to_datetime(df['Gyűjtési dátum'], format='mixed')

        df = df.drop(columns=['Gyűjtési dátum'])
        df.set_index('Date', inplace=True)

        return df

    def transform_indices_monthly_period(self) -> pd.DataFrame:
        """
        Adjusts the DataFrame indices based on the collection dates.

        This method converts the 'Gyűjtési dátum' to a period format (monthly),
        groups the data by date, and aggregates the columns accordingly.
        Additionally, it reindexes the DataFrame to cover the full date range.
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
            **{col: 'sum' for col in self.data.columns if col not in ['Date',
                                                                      'Min - T (°C)', 'Max - T (°C)', 'Min - RH(%)',
                                                                      'Max - RH(%)', 'Gyűjtés helye']}
        }).reset_index()

        df.set_index('Date', inplace=True)
        df.index = df.index.to_period('M')

        return df
