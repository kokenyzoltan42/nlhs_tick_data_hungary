import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc.basis_variance_calculator import BasisVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.correlation_calculator import CorrelationCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.log_ratio_variance_calculator import \
    LogRatioVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.strongly_correlated_pair_excluder import \
    StronglyCorrelatedPairHandler


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
            variation_matrix = log_ratio_variances.result.copy()
            num_of_components = variation_matrix.shape[1]

            # Initialize helper matrix for variance calculations
            helper_matrix = (np.ones((num_of_components, num_of_components)) +
                             np.diag([num_of_components - 2] * num_of_components))

            # Compute basis variances
            basis_variances = BasisVarianceCalculator(log_ratio_variance=variation_matrix,
                                                      helper_matrix=helper_matrix)
            basis_variances.run()

            # Compute correlations
            correlation_calculator = CorrelationCalculator(basis_variances=basis_variances.result,
                                                           log_ratio_variance=variation_matrix)
            correlation_calculator.run()
            correlations = correlation_calculator.result.copy()

            # Iteratively remove strongly correlated pairs
            iterative_process = StronglyCorrelatedPairHandler(variation_matrix=variation_matrix,
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
