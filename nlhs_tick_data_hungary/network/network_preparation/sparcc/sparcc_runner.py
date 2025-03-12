import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import StronglyCorrelatedPairExcluder


class SparCCRunner:
    def __init__(self, df: pd.DataFrame, args: dict):
        self.df = df
        self.args = args

        self.data = None

    def run(self) -> pd.DataFrame:
        # List to store computed correlations
        correlations = []
        for _ in range(self.args['n_iter']):
            print('N_iter: ' + str(_))
            # Resampling data with dirichlet
            self.resample_data_with_dirichlet()
            # Calculate the correlations and exclude components that violate the conditions of the algorithm
            strongly_correlated_pair_excluder = StronglyCorrelatedPairExcluder(data=self.data,
                                                                               x_iter=self.args['x_iter'],
                                                                               threshold=self.args['threshold'])
            strongly_correlated_pair_excluder.run()
            # Storing the results of the algorithm
            correlations.append(strongly_correlated_pair_excluder.result)
        # Return the median of the correlations
        return np.nanmedian(np.array(correlations), axis=0)

    def resample_data_with_dirichlet(self):
        """
        Resample the data using a Dirichlet distribution applied row-wise.

        Each row of the data is treated as the parameters for the Dirichlet distribution,
        which generates(?) a new row of samples based on those parameters.
        """
        self.data = np.apply_along_axis(
            lambda x: np.random.mtrand.dirichlet(x + 1),
            axis=0,
            arr=self.df
        )
