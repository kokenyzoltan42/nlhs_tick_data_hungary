import json

import pandas as pd
from pandas import DataFrame

from nlhs_tick_data_hungary import config_path
from nlhs_tick_data_hungary.data.utils.google_sheet_dataloader import GoogleSheetDataLoader
from nlhs_tick_data_hungary.data.data_preprocessing.pilis.pilis_tick_data_preprocessor import PilisTickDataPreprocessor


class PilisTickDataLoader:
    def __init__(self):
        self.result = None

        with open(config_path + f'/links.json', 'r+') as file:
            self.links = json.load(file)

        self.run()

    def run(self) -> None:
        raw_pilis_tick_data = self.load_raw_data()
        self.result = self.preprocess_data(raw_pilis_tick_data=raw_pilis_tick_data)

    def load_raw_data(self) -> pd.DataFrame:

        dataloader = GoogleSheetDataLoader(url=self.links['pilis_tick'])
        return dataloader.load_data()

    @staticmethod
    def preprocess_data(raw_pilis_tick_data: pd.DataFrame) -> dict[DataFrame, DataFrame]:
        preprocessor = PilisTickDataPreprocessor(raw_pilis_tick_data=raw_pilis_tick_data)

        preprocessor.run()

        return preprocessor.result
