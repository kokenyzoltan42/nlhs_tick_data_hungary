import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc.basis_variance_calculator import BasisVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.correlation_calculator import CorrelationCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.log_ratio_variance_calculator import \
    LogRatioVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.strongly_correlated_pair_excluder import StronglyCorrelatedPairHandler


class SparCCRunner:
    def __init__(self, df: pd.DataFrame, args: dict):
        # Original data
        self.df = df
        self.args = args

        # Attribute to store resampled data
        self.data = None

    def run(self) -> pd.DataFrame:
        correlation_results = []

        for _ in range(self.args['n_iter']):
            self.estimate_component_fractions()
            log_ratio_variances = LogRatioVarianceCalculator(data=self.data)
            log_ratio_variances.run()
            variation_matrix = log_ratio_variances.result.copy()
            num_of_components = variation_matrix.shape[1]

            helper_matrix = (np.ones((num_of_components, num_of_components)) +
                             np.diag([num_of_components - 2] * num_of_components))

            basis_variances = BasisVarianceCalculator(log_ratio_variance=variation_matrix,
                                                      helper_matrix=helper_matrix)
            basis_variances.run()
            correlation_calculator = CorrelationCalculator(basis_variances=basis_variances.result,
                                                           log_ratio_variance=variation_matrix)
            correlation_calculator.run()
            correlations = correlation_calculator.result.copy()

            iterative_process = StronglyCorrelatedPairHandler(variation_matrix=variation_matrix,
                                                              correlations=correlations,
                                                              helper_matrix=helper_matrix,
                                                              exclusion_threshold=self.args['threshold'],
                                                              exclusion_iterations=self.args['x_iter'])

            iterative_process.calc_correlations_with_sparcc()
            correlation_results.append(correlations)

        return np.nanmedian(np.array(correlation_results), axis=0)

    def estimate_component_fractions(self):
        """
        Resample the data using a Dirichlet distribution applied row-wise.

        Each row of the data is treated as the parameters for the Dirichlet distribution,
        which generates(?) a new row of samples based on those parameters.
        """
        np.random.seed(42)
        self.data = np.apply_along_axis(
            lambda x: np.random.mtrand.dirichlet(x + 1),
            axis=1,
            arr=self.df
        )
