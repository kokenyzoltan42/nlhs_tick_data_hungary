from typing import Tuple

import pandas as pd


class PilisTickDataLoader:
    def __init__(self):
        pass

    def run(self) -> None:
        pass

    def load_raw_data(self) -> pd.DataFrame:
        pass

    def preprocess_data(self, raw_pilis_tick_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pass
