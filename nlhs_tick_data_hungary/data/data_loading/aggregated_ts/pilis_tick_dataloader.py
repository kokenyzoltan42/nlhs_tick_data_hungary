import os
import pickle
import typing

import pandas as pd

from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.core_dataloader import CoreDataLoader
from nlhs_tick_data_hungary.data.utils.google_sheet_dataloader import GoogleSheetDataLoader
from nlhs_tick_data_hungary.data.data_preprocessing.pilis.pilis_tick_data_preprocessor import PilisTickDataPreprocessor


class PilisTickDataLoader(CoreDataLoader):
    """
    A class to load and preprocess tick data from a Google Sheets source.
    """

    def __init__(self, use_cache: bool = False):
        """
        Initializes the PilisTickDataLoader.

        This constructor calls the `run` method to automatically load and process
        tick data collected from the Pilis region upon initialization.

        :param bool use_cache: Whether to load the data from the cached files.
        """
        super().__init__(use_cache=use_cache)
        self.run()

    def run(self) -> None:
        """
        Runs the data loading and preprocessing pipeline:
        - Loads the raw Pilis tick data from Google Sheets.
        - Preprocesses the data and stores the result.
        """
        cache_file = 'cache/pilis_tick_data.pkl'
        if self.use_cache and os.path.exists(cache_file):
            # If the cache is enabled AND the file exists, load it
            with open(cache_file, 'rb') as f:
                self.result = pickle.load(f)
        else:
            # Load the raw tick data from the Google Sheets using the links from the config file
            raw_pilis_tick_data = self.load_raw_data()

            # Preprocess the raw data and store it
            self.result = self.preprocess_data(raw_pilis_tick_data=raw_pilis_tick_data)
            # Make a directory for saving the results in a `.pkl` file
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            # Save processed data to a `.pkl` file
            with open(cache_file, 'wb') as f:
                pickle.dump(self.result, f)

    def load_raw_data(self) -> pd.DataFrame:
        """
        Loads the raw Pilis tick data from the specified Google Sheets file.

        The raw data is loaded using the GoogleSheetDataLoader class, which downloads
        the data from a URL and returns it as a pandas DataFrame.

        :return pd.DataFrame: The raw Pilis tick data loaded from Google Sheets.
        """
        # Use the GoogleSheetDataLoader to download and load the data from the specified URL
        dataloader = GoogleSheetDataLoader(url=self.links['pilis_tick'])

        return dataloader.load_data()

    @staticmethod
    def preprocess_data(raw_pilis_tick_data: pd.DataFrame) -> typing.Dict[str, pd.DataFrame]:
        """
        Preprocesses the raw Pilis tick data by running it through the PilisTickDataPreprocessor.

        This method initializes the PilisTickDataPreprocessor to processes the raw data,
        and returns the processed result. The result is a dictionary with two dataframes:
        - dataframe with modified (monthly) indices
        - dataframe with the original dates

        :param pd.DataFrame raw_pilis_tick_data: The raw tick data to be preprocessed.

        :return typing.Dict[str, pd.DataFrame]: A dictionary containing the preprocessed data.
         The keys will correspond to different stages or categories of the processed data,
         and the values will be the corresponding pandas DataFrames.
        """
        # Initialize and run the preprocessor with the raw tick data
        preprocessor = PilisTickDataPreprocessor(raw_pilis_tick_data=raw_pilis_tick_data)
        preprocessor.run()

        return preprocessor.result
