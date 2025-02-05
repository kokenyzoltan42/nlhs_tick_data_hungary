from typing import Tuple

import pandas as pd

from nlhs_tick_data_hungary.data.data_preprocessing.pilis.column_transformer import ColumnTransformer
from nlhs_tick_data_hungary.data.data_preprocessing.pilis.index_transformer import IndexTransformer


class PilisTickDataPreprocessor:
    def __init__(self, raw_data: pd.DataFrame):
        self.raw_data = raw_data

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pass

    def fill_missing_data(self) -> pd.DataFrame:
        pass

    def sum_species(self):
        pass
