import os
import pickle
import typing

import pandas as pd

from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.core_dataloader import CoreDataLoader
from nlhs_tick_data_hungary.data.utils.google_sheet_dataloader import GoogleSheetDataLoader
from ...data_preprocessing.winter_tick.winter_tick_data_preprocessor import WinterTickDataPreprocessor


class WinterTickDataLoader(CoreDataLoader):
    """
    A class responsible for loading winter tick data.

    This class loads raw winter tick data from a Google Sheet, preprocesses it using the `WinterTickDataPreprocessor`,
    and stores the resulting processed data.

    Structure of the `data` attribute after the `run` method is called:
        `self.data` = {
            'every_bacteria': a pd.DataFrame containing the data of every bacterium
            'removed_catch_all': a pd.DataFrame containing the data of every bacterium except the ones whose name
                                contain 'catch all'
            'group_1': a pd.DataFrame containing the data of every bacterium from the "first group"
            'group_2': a pd.DataFrame containing the data of every bacterium from the "second group"
            'group_3': a pd.DataFrame containing the data of every bacterium from the "third group"
        }
    """

    def __init__(self, use_cache: bool = False):
        """
        Initializes the WinterTickDataLoader class by setting up the `result` attribute to store processed data
        and loading the links to the necessary datasets.

        :param bool use_cache: Whether to load the data from the cached files.
        """
        super().__init__(use_cache=use_cache)
        self.run()

    def run(self) -> None:
        """
        Runs the data loading and preprocessing pipeline.

        Loads the raw winter tick data from the Google Sheet using the `load_raw_data` method then preprocesses the
        raw data using the `preprocess_data` method and stores the result in the `result` attribute.
        """
        cache_file = 'cache/winter_tick_data.pkl'

        if self.use_cache and os.path.exists(cache_file):
            # If the cache is enabled AND the file exists, load it
            with open(cache_file, 'rb') as f:
                self.result = pickle.load(f)
        else:
            # Load raw data
            raw_data = self.load_raw_data()

            # Preprocess the raw data and store the result
            self.result = self.preprocess_data(raw_data=raw_data)

            # Make a directory for saving the results in a `.pkl` file
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            # Save processed data to a `.pkl` file
            with open(cache_file, 'wb') as f:
                pickle.dump(self.result, f)

    def load_raw_data(self) -> pd.DataFrame:
        """
        Loads raw winter tick data from a Google Sheet.
        This method uses the `GoogleSheetDataLoader` class to get data from the provided URL stored in `links.json`.

        :return: A pandas DataFrame containing the raw winter tick data.
        """
        # Initialize GoogleSheetDataLoader with the URL from the configuration file
        dataloader = GoogleSheetDataLoader(url=self.links['winter_tick'])

        # Load the data from the Google Sheet and return it as a DataFrame
        return dataloader.load_data()

    @staticmethod
    def preprocess_data(raw_data: pd.DataFrame) -> typing.Dict[str, pd.DataFrame]:
        """
        Preprocesses the raw winter tick data.

        This method creates an instance of `WinterTickDataPreprocessor`, which handles the data cleaning,
        transformation, and other preprocessing steps. It then returns the processed data.

        :param pd.DataFrame raw_data: A pandas DataFrame containing the raw winter tick data to be processed.
        :return dict: A dictionary containing the processed winter tick datas.
        """
        # Initialize the preprocessor with the raw data
        preprocessor = WinterTickDataPreprocessor(data=raw_data)

        # Run the preprocessing steps
        preprocessor.run()

        # Return the processed result
        return preprocessor.result
