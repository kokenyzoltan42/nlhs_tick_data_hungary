import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import StronglyCorrelatedPairExcluder


class SparCCRunner:
    def __init__(self, df: pd.DataFrame, args: dict):
        self.df = df
        self.args = args

    def run(self) -> pd.DataFrame:
        correlations = []
        for ni in self.args['n_iter']:
            strongly_correalted_pair_excluder = StronglyCorrelatedPairExcluder(data=self.df,
                                                                               x_iter=self.args['x_iter'],
                                                                               tol=self.args['tol'])
            strongly_correalted_pair_excluder.run()
            correlations.append(strongly_correalted_pair_excluder.result)

        return np.nanmedian(np.array(correlations), axis=0)
