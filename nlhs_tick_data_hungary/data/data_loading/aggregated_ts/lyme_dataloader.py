import os
import pickle

import pandas as pd

from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.core_dataloader import CoreDataLoader
from nlhs_tick_data_hungary.data.utils.google_data_downloader import GoogleDataDownloader


class LymeDataLoader(CoreDataLoader):
    """
    A class to load and process Lyme disease data from `.csv` files stored on Google Drive.
    The data is loaded, processed by year or month, and stored in a dictionary.

    result (dict): A dictionary that stores the processed Lyme disease data,
                   organized by year and month.
    links (dict): A dictionary containing the URLs for the raw Lyme disease data files.
    """
    def __init__(self, use_cache: bool = False):
        """
        Initializes the LymeDataLoader.

        This constructor calls the `run` method to automatically load and process
        Lyme disease data upon initialization.

        :param bool use_cache: Whether to load the data from the cached files.
        """
        super().__init__(use_cache=use_cache)
        self.run()

    def run(self) -> None:
        """
        Runs the data loading and processing pipeline:
        - Loads the raw Lyme disease data (monthly and yearly).
        - Processes the data and organizes it into a dictionary.
        """
        cache_file = 'cache/lyme_data.pkl'

        if self.use_cache and os.path.exists(cache_file):
            # If the cache is enabled AND the file exists, load it
            with open(cache_file, 'rb') as f:
                self.result = pickle.load(f)
        else:
            # Load the raw Lyme data from Google Drive using the links from the config file
            lyme_raw = self.load_lyme_data()

            # Process the raw data and store the results
            self.result = {
                'lyme_year': self.preprocess_data(lyme_data=lyme_raw['lyme_year'], period='Y'),
                'lyme_month': self.preprocess_data(lyme_data=lyme_raw['lyme_month'], period='M'),
            }
            # Make a directory for saving the results in a `.pkl` file
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            # Save processed data to a `.pck` file
            with open(cache_file, 'wb') as f:
                pickle.dump(self.result, f)

    def load_lyme_data(self) -> dict:
        """
        Downloads the raw Lyme disease data files from Google Drive and loads them into pandas DataFrames.

        :return dict: A dictionary containing the raw Lyme disease data for both monthly and yearly periods.
                  The keys are 'lyme_month' and 'lyme_year', and the values are the corresponding DataFrames.
        """
        # Download the Lyme disease monthly data using the GoogleDataDownloader
        lyme_month_drive = GoogleDataDownloader(
            file_url=self.links["lyme_month"],
            file_name="lyme_disease_monthly.csv")

        # Download the Lyme disease yearly data using the GoogleDataDownloader
        lyme_year_drive = GoogleDataDownloader(
            file_url=self.links["lyme_year"],
            file_name="lyme_disease_yearly.csv")

        # Read the `.csv` files into pandas DataFrames
        lyme_raw = {
            'lyme_month': pd.read_csv(lyme_month_drive.file_path),
            'lyme_year': pd.read_csv(lyme_year_drive.file_path),
        }

        return lyme_raw

    @staticmethod
    def preprocess_data(lyme_data: pd.Series, period: str) -> pd.Series:
        """
        Processes Lyme disease data by formatting the 'Date' column and converting it into a pandas Series indexed
        by the specified period (monthly or yearly).

        :param pd.Series lyme_data: The raw Lyme disease data to be processed, with a 'Date' column and 'Values'.
        :param str period: The period type for the data ('M' for monthly, 'Y' for yearly).

        :return pd.Series: A pd.Series indexed by the specified period (monthly or yearly), containing the 'Values'.
        """
        # Determine the time format based on the period type (monthly or yearly)
        time_format = None

        if period == 'Y':
            time_format = '%Y'
        if period == 'M':
            time_format = '%Y-%m'

        # Convert the 'Date' column to datetime and set it as the index
        lyme_data['Date'] = pd.to_datetime(lyme_data['Date'], format=time_format)
        lyme_data.set_index(keys='Date', inplace=True)

        # Convert the DataFrame index to a period index
        lyme_data = lyme_data.to_period(period)

        # Return the data as a Series
        return pd.Series(index=lyme_data.index, data=lyme_data['Values'])
