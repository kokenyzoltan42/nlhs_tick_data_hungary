import json

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary import config_path
from nlhs_tick_data_hungary.data.utils.google_data_downloader import GoogleDataDownloader


class RainfallDataLoader:
    """
    A class to load and preprocess rainfall data from Google Sheets for two locations: Piliscsaba and Pilisszentkereszt.
    The data is processed into pandas Series, handling missing values and time indexing.

    result (dict): A dictionary containing processed rainfall data for the specified locations.
    links (dict): A dictionary containing the URLs for the rainfall data files
                  (for Piliscsaba and Pilisszentkereszt).
    """

    def __init__(self):
        """
        Initializes the Rainfall by loading the URLs for the tick data file and then runs the data loading
        and preprocessing.
        """
        self.result = None

        # Load the links for the rainfall data files from the 'links.json' config file
        with open(config_path + f'/links.json', 'r+') as file:
            self.links = json.load(file)

        self.run()

    def run(self) -> None:
        """
        Runs the data loading and processing pipeline:
        - Loads the raw rainfall data for Piliscsaba and Pilisszentkereszt.
        - Processes the data and stores the result.
        """
        # Load the raw rainfall data for both locations
        raw_rainfall_data = self.load_rainfall_data()

        # Process the raw rainfall data for both locations and store the results
        self.result = {
            'piliscsaba': self.process_rainfall_data(raw_rainfall_data['piliscsaba']),
            'pilisszentkereszt': self.process_rainfall_data(raw_rainfall_data['pilisszentkereszt']),
        }

    def load_rainfall_data(self) -> dict:
        """
        Loads the raw rainfall data from the specified Google Sheets files.

        The raw data for each location (Piliscsaba and Pilisszentkereszt) are loaded into pandas DataFrames.

        :return dict: A dictionary containing lists of DataFrames for both Piliscsaba and Pilisszentkereszt.
                  The keys are 'piliscsaba' and 'pilisszentkereszt', and the values are lists of DataFrames.
        """
        # Download rainfall data for Piliscsaba (2002-2023 and 2024)
        g_dl_piliscsaba_2002_2023 = GoogleDataDownloader(
            file_url=self.links["piliscsaba_csapadek_2002-2023"],
            file_name="piliscsaba_2002-2023.csv"
        )
        g_dl_piliscsaba_2024 = GoogleDataDownloader(
            file_url=self.links["piliscsaba_csapadek_2024"],
            file_name="piliscsaba_csapadek_2024.csv"
        )

        # Load the raw data for Piliscsaba
        raw_piliscsaba_2002_2023 = pd.read_csv(g_dl_piliscsaba_2002_2023.file_path, sep=';', header=4)
        raw_piliscsaba_2024 = pd.read_csv(g_dl_piliscsaba_2024.file_path, sep=';', header=4)

        # Download rainfall data for Pilisszentkereszt (2020-2023 and 2024)
        g_dl_pilisszentkereszt_2020_2023 = GoogleDataDownloader(
            file_url=self.links["pilisszentkereszt_csapadek_2020-2023"],
            file_name="pilisszentkereszt_csapadek_2020-2023"
        )
        g_dl_pilisszentkereszt_2024 = GoogleDataDownloader(
            file_url=self.links["pilisszentkereszt_csapadek_2024"],
            file_name="pilisszentkereszt_csapadek_2024.csv"
        )

        # Load the raw data for Pilisszentkereszt
        raw_pilisszentkereszt_2020_2023 = pd.read_csv(g_dl_pilisszentkereszt_2020_2023.file_path, sep=';', header=4)
        raw_pilisszentkereszt_2024 = pd.read_csv(g_dl_pilisszentkereszt_2024.file_path, sep=';', header=4)

        return {
            'piliscsaba': [raw_piliscsaba_2002_2023, raw_piliscsaba_2024],
            'pilisszentkereszt': [raw_pilisszentkereszt_2020_2023, raw_pilisszentkereszt_2024]
        }

    @staticmethod
    def process_rainfall_data(rainfall_datas: list) -> pd.Series:
        """
        Processes the raw rainfall data by cleaning and combining the data into a single pandas Series.

        :param rainfall_datas: A list of pandas DataFrames, each containing raw rainfall data.

        :return pd.Series: A pandas Series containing the processed rainfall data, indexed by the 'Time' column.
        """
        rainfall_series = {}

        for idx, data in enumerate(rainfall_datas):
            # Remove unnecessary whitespaces from the column names
            data.columns = data.columns.str.strip()

            # Convert the 'Time' column to datetime and set it as the index
            data['Time'] = pd.to_datetime(data["Time"], format='%Y%m%d')
            data.set_index('Time', inplace=True)

            # Replace missing values (-999) with NaN
            data.replace(-999, np.nan, inplace=True)

            # Ensure the 'r' column is treated as a numeric Series
            rainfall_series[idx] = data['r'].astype(float)

        # Concatenate all the processed data into a single Series and sort by time index
        processed_series = pd.concat(rainfall_series.values()).sort_index().squeeze()

        return processed_series
