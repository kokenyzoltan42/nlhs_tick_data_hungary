import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.sparcc.correlation_updater import CorrelationUpdater
from nlhs_tick_data_hungary.network import LogRatioVarianceCalculator
from nlhs_tick_data_hungary.network import StronglyCorrelatedPairHandler


class SparCCRunner:
    """
    Executes the SparCC algorithm on input data, iteratively estimating correlation matrices.
    Handles resampling, variance computation, and iterative correlation exclusion.
    """

    def __init__(self, df: pd.DataFrame, args: dict):
        """
        Initializes the SparCCRunner with data and algorithm parameters.

        :param pd.DataFrame df: Input dataframe containing compositional data.
        :param dict args: Dictionary of parameters controlling the number of iterations, threshold, and exclusions.
        """
        # Original data
        self.df = df
        self.args = args

        # Attribute to store resampled data
        self.data = None

    def run(self) -> pd.DataFrame:
        """
        Executes the SparCC correlation estimation algorithm over multiple iterations.

        :return: Median correlation matrix computed over all iterations.
        """
        correlation_results = []

        for _ in range(self.args['n_iter']):
            self.estimate_component_fractions()

            # Compute log-ratio variances
            log_ratio_variances = LogRatioVarianceCalculator(data=self.data)
            log_ratio_variances.run()
            log_ratio_variances = log_ratio_variances.result.copy()
            num_of_components = log_ratio_variances.shape[1]

            # Initialize helper matrix for variance calculations
            helper_matrix = (np.ones((num_of_components, num_of_components)) +
                             np.diag([num_of_components - 2] * num_of_components))

            # Compute correlations
            correlations = CorrelationUpdater.calculate_correlation(
                log_ratio_variances=log_ratio_variances,
                helper_matrix=helper_matrix
            )

            # Iteratively remove strongly correlated pairs
            iterative_process = StronglyCorrelatedPairHandler(log_ratio_variances=log_ratio_variances,
                                                              correlations=correlations,
                                                              helper_matrix=helper_matrix,
                                                              exclusion_threshold=self.args['threshold'],
                                                              exclusion_iterations=self.args['x_iter'])

            iterative_process.run()
            correlation_results.append(correlations)

        # Compute the median correlation matrix across iterations
        return np.nanmedian(np.array(correlation_results), axis=0)

    def estimate_component_fractions(self):
        """
        Resample the data using a Dirichlet distribution applied row-wise.

        Each row of the dataset is treated as a parameter vector for the Dirichlet distribution,
        generating new resampled compositions while preserving the compositional nature of the data.
        """
        self.data = np.apply_along_axis(
            lambda x: np.random.mtrand.dirichlet(x + 1),
            axis=1,
            arr=self.df
        )
