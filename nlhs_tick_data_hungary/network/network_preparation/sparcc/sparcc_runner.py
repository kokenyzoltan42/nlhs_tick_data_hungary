import pandas as pd


class SparCCRunner:
    def __init__(self, df: pd.DataFrame, args: dict):
        self.df = df
        self.args = args

    def run(self) -> pd.DataFrame:
        pass
