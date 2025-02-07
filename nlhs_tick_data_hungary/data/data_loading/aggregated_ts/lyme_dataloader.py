import json

import pandas as pd

from nlhs_tick_data_hungary import config_path
from nlhs_tick_data_hungary.data.utils.google_data_downloader import GoogleDataDownloader


# TODO: add docstrings
class LymeDataLoader:
    def __init__(self):
        self.result = None

        with open(config_path + f'/links.json', 'r+') as file:
            self.links = json.load(file)

        self.run()

    def run(self) -> None:

        lyme_raw = self.load_lyme_data()

        self.result = {
            'lyme_year': self.process_lyme_data(lyme_data=lyme_raw['lyme_year'], period='Y'),
            'lyme_month': self.process_lyme_data(lyme_data=lyme_raw['lyme_month'], period='M'),
        }

    def load_lyme_data(self) -> dict:
        lyme_month_drive = GoogleDataDownloader(
            file_url=self.links["lyme_month"],
            file_name="lyme_disease_monthly.csv")
        lyme_year_drive = GoogleDataDownloader(
            file_url=self.links["lyme_year"],
            file_name="lyme_disease_yearly.csv")

        lyme_raw = {
            'lyme_month': pd.read_csv(lyme_month_drive.file_path),
            'lyme_year': pd.read_csv(lyme_year_drive.file_path),
        }

        return lyme_raw

    @staticmethod
    def process_lyme_data(lyme_data: pd.Series, period: str) -> pd.Series:
        # TODO: change docstring
        """
        Loads Lyme disease data from a CSV file, formats the date and converts it into a Series.

        :param path: Path to the CSV file containing Lyme disease data.
        :param period: The period type for the data ('M' for monthly, 'Y' for yearly).
        :return: A pandas Series indexed by the specified time period.
        """

        # Determine the time format based on the period type (monthly or yearly)
        time_format = None

        if period == 'Y':
            time_format = '%Y'
        if period == 'M':
            time_format = '%Y-%m'

        # Convert the 'Date' column to a datetime object and set it as index
        lyme_data['Date'] = pd.to_datetime(lyme_data['Date'], format=time_format)
        lyme_data.set_index(keys='Date', inplace=True)

        # Convert the DataFrame index to a period index (e.g., monthly or yearly)
        lyme_data = lyme_data.to_period(period)

        # Return the data as a Series
        lyme_series = pd.Series(index=lyme_data.index, data=lyme_data['Values'])

        return lyme_series
