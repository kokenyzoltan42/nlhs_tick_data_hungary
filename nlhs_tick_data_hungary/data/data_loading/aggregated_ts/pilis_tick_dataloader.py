import json

import pandas as pd

from nlhs_tick_data_hungary import config_path
from nlhs_tick_data_hungary.data.utils.google_sheet_dataloader import GoogleSheetDataLoader
from nlhs_tick_data_hungary.data.data_preprocessing.pilis.pilis_tick_data_preprocessor import PilisTickDataPreprocessor


class PilisTickDataLoader:
    """
    A class to load and preprocess tick data from a Google Sheets source.

    result (dict): A dictionary that stores the processed tick data after preprocessing.
    links (dict): A dictionary containing the URLs for the raw data (in Google Sheets).
    """

    def __init__(self):
        """
        Initializes the PilisTickDataLoader by loading the URLs for the tick data file and then runs the data loading
        and preprocessing.
        """
        self.result = None

        # Load the links for the Pilis tick data from the 'links.json' config file
        with open(config_path + f'/links.json', 'r+') as file:
            self.links = json.load(file)

        self.run()

    def run(self) -> None:
        """
        Runs the data loading and preprocessing pipeline:
        - Loads the raw Pilis tick data from Google Sheets.
        - Preprocesses the data and stores the result.
        """
        # Load the raw tick data from the Google Sheets using the links from the config file
        raw_pilis_tick_data = self.load_raw_data()

        # Preprocess the raw data and store it
        self.result = self.preprocess_data(raw_pilis_tick_data=raw_pilis_tick_data)

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
    def preprocess_data(raw_pilis_tick_data: pd.DataFrame) -> dict[pd.DataFrame, pd.DataFrame]:
        """
        Preprocesses the raw Pilis tick data by running it through the PilisTickDataPreprocessor.

        This method initializes the PilisTickDataPreprocessor to processes the raw data,
        and returns the processed result. The result is a dictionary with two dataframes:
        - dataframe with modified (monthly) indices
        - dataframe with the original dates

        :param raw_pilis_tick_data: The raw tick data to be preprocessed.

        :return dict: A dictionary containing the preprocessed data. The keys will likely correspond to different stages
         or categories of the processed data, and the values will be the corresponding pandas DataFrames.
        """
        # Initialize and run the preprocessor with the raw tick data
        preprocessor = PilisTickDataPreprocessor(raw_pilis_tick_data=raw_pilis_tick_data)
        preprocessor.run()

        return preprocessor.result
