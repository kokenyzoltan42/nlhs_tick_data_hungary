import json

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary import url_path
from nlhs_tick_data_hungary.data.utils.google_data_downloader import GoogleDataDownloader


# TODO: importokat __init__.py-ba?

class RainfallDataLoader:
    def __init__(self):
        self.result = None

        with open(url_path + f'/links.json', 'r+') as file:
            self.links = json.load(file)

    def run(self) -> None:
        raw_rainfall_data = self.load_rainfall_data()

        self.result = {
            'piliscsaba': self.process_rainfall_data(raw_rainfall_data['piliscsaba']),
            'pilisszentkereszt': self.process_rainfall_data(raw_rainfall_data['pilisszentkereszt']),
        }

    def load_rainfall_data(self) -> dict:
        g_dl_piliscsaba_2002_2023 = GoogleDataDownloader(
            file_url=self.links["piliscsaba_csapadek_2002-2023"],
            file_name="piliscsaba_2002-2023.csv"
        )
        g_dl_piliscsaba_2024 = GoogleDataDownloader(
            file_url=self.links["piliscsaba_csapadek_2024"],
            file_name="piliscsaba_csapadek_2024.csv"
        )
        raw_piliscsaba_2020_2023 = pd.read_csv(g_dl_piliscsaba_2002_2023.file_path, sep=';', header=4)
        raw_piliscsaba_2024 = pd.read_csv(g_dl_piliscsaba_2024.file_path, sep=';', header=4)

        g_dl_pilisszentkereszt_2020_2023 = GoogleDataDownloader(
            file_url=self.links["pilisszentkereszt_csapadek_2020-2023"],
            file_name="pilisszentkereszt_csapadek_2020-2023"
        )
        g_dl_pilisszentkereszt_2024 = GoogleDataDownloader(
            file_url=self.links["pilisszentkereszt_csapadek_2024"],
            file_name="pilisszentkereszt_csapadek_2024.csv"
        )
        raw_pilisszentkereszt_2020_2023 = pd.read_csv(g_dl_pilisszentkereszt_2020_2023.file_path, sep=';', header=4)
        raw_pilisszentkereszt_2024 = pd.read_csv(g_dl_pilisszentkereszt_2024.file_path, sep=';', header=4)

        return {
            'piliscsaba': [raw_piliscsaba_2020_2023, raw_piliscsaba_2024],
            'pilisszentkereszt': [raw_pilisszentkereszt_2020_2023, raw_pilisszentkereszt_2024]
        }

    @staticmethod
    def process_rainfall_data(rainfall_data: dict) -> pd.Series:
        rainfall_series = {}

        for item in rainfall_data:
            # Remove unnecessary whitespaces from the columns
            rainfall_data[item].columns = rainfall_data[item].columns.str.strip()

            # Create time index
            rainfall_data[item]['Time'] = pd.to_datetime(rainfall_data[item]["Time"], format='%Y%m%d')
            rainfall_data[item].set_index('Time', inplace=True)

            # Replace missing values with NaN
            rainfall_data[item].replace(-999, np.nan, inplace=True)

            # Ensure the 'r' column is treated as a Series
            rainfall_series[item] = rainfall_data[item]['r'].astype(float)

        # Concatenate into a single Series
        processed_series = pd.concat(rainfall_series.values()).sort_index().squeeze()
        # TODO: letesztelni, hogy működik-e így a squeeze

        return processed_series
