from typing import Tuple

import pandas as pd


class ColumnTransformer:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def run(self) -> None:
        pass

    def rename_unnamed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @staticmethod
    def split_min_max(series: pd.Series) -> Tuple[pd.Series, pd.Series]: # Lehet, hogy nem Tuple, csak Series
        pass

    def split_temps_and_rhs(self) -> None:
        pass
