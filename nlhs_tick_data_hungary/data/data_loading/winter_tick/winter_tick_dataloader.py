import json

import pandas as pd

from nlhs_tick_data_hungary import config_path
from nlhs_tick_data_hungary.data.utils.google_sheet_dataloader import GoogleSheetDataLoader
from ...data_preprocessing.winter_tick.winter_tick_data_preprocessor import WinterTickDataPreprocessor


class WinterTickDataLoader:
    def __init__(self):
        self.result = {}

        with open(config_path + f'/links.json', 'r+') as file:
            self.links = json.load(file)

    def run(self) -> None:
        raw_data = self.load_raw_data()
        self.result = self.preprocess_data(raw_data=raw_data)

    def load_raw_data(self) -> pd.DataFrame:
        dataloader = GoogleSheetDataLoader(url=self.links['winter_tick'])
        return dataloader.load_data()

    @staticmethod
    def preprocess_data(raw_data: pd.DataFrame) -> dict:
        preprocessor = WinterTickDataPreprocessor(data=raw_data)
        preprocessor.run()

        return preprocessor.result
