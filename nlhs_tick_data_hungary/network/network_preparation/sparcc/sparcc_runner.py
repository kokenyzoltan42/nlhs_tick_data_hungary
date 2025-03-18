from typing import Tuple

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc.basis_variance_calculator import BasisVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.correlation_calculator import CorrelationCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.log_ratio_variance_calculator import \
    LogRatioVarianceCalculator


class SparCCRunner:
    def __init__(self, df: pd.DataFrame, args: dict):
        self.df = df
        self.args = args

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

            iterative_process = IterativeExclusion(variation_matrix=variation_matrix,
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


class IterativeExclusion:
    def __init__(self, variation_matrix: np.ndarray, correlations: np.ndarray, helper_matrix: np.ndarray,
                 exclusion_threshold: float, exclusion_iterations: int):
        self.variation_matrix = variation_matrix
        self.correlations = correlations
        self.helper_matrix = helper_matrix
        self.exclusion_threshold = exclusion_threshold
        self.exclusion_iterations = exclusion_iterations

        self.num_of_components = variation_matrix.shape[1]
        self.variation_matrix_copy = self.variation_matrix.copy()
        self.excluded_pairs = []
        self.excluded_components = np.array([])

    def calc_correlations_with_sparcc(self):
        for _ in range(self.exclusion_iterations):
            to_exclude = self.find_new_excluded_pair()
            if to_exclude is None:
                break

            self.excluded_pairs.append(to_exclude)
            i, j = to_exclude

            self.helper_matrix[i, j] -= 1
            self.helper_matrix[j, i] -= 1
            self.helper_matrix[i, i] -= 1
            self.helper_matrix[j, j] -= 1

            inds = tuple(zip(*self.excluded_pairs))
            self.variation_matrix[inds] = 0
            self.variation_matrix.T[inds] = 0

            self.exclude_components()

            another_basis_variance_calculator = BasisVarianceCalculator(log_ratio_variance=self.variation_matrix,
                                                                        helper_matrix=self.helper_matrix)
            another_basis_variance_calculator.run()
            basis_variances = another_basis_variance_calculator.result
            another_correlation_calculator = CorrelationCalculator(log_ratio_variance=self.variation_matrix,
                                                                   # Ennek szigorún ennek kell lennie
                                                                   basis_variances=basis_variances)
            another_correlation_calculator.run()
            self.correlations = another_correlation_calculator.result

            for excluded_component in self.excluded_components:
                self.correlations[excluded_component, :] = np.nan
                self.correlations[:, excluded_component] = np.nan

    def find_new_excluded_pair(self) -> Tuple[int, int] | None:
        """
        Identifies the most correlated pair in the dataset that has not yet been excluded.
        """
        # Consider only the upper triangle of the correlation matrix (excluding diagonal)
        corr_temp = np.triu(np.abs(self.correlations), 1)
        if self.excluded_pairs:
            corr_temp[tuple(zip(*self.excluded_pairs))] = 0  # Exclude already removed pairs

        # Find the most correlated pair
        i, j = np.unravel_index(np.argmax(corr_temp), corr_temp.shape)
        corr_max = corr_temp[i, j]

        # Return the pair if it exceeds the threshold, otherwise return None
        return (i, j) if corr_max > self.exclusion_threshold else None

    def exclude_components(self):
        """
        Identifies and excludes components that have been involved in too many exclusions, based on a predefined
        threshold. Updates the helper matrix accordingly.
        """
        # Count occurrences of each component in excluded pairs
        num_of_excluded = np.bincount(np.ravel(self.excluded_pairs))
        previously_excluded_components = set(self.excluded_components.copy())
        # Identify components that have been excluded too many times
        self.excluded_components = set(np.where(num_of_excluded >= self.num_of_components - 3)[0])
        newly_excluded_components = self.excluded_components - previously_excluded_components

        if newly_excluded_components:
            # If too many components are excluded, raise an error
            if len(self.excluded_components) > (self.num_of_components - 4):
                raise ValueError("Too many components had to be excluded from the analysis")
            # Update the helper matrix to remove newly excluded components
            for comp in newly_excluded_components:
                self.variation_matrix[comp, :] = 0
                self.variation_matrix[:, comp] = 0
                self.helper_matrix[comp, :] = 0
                self.helper_matrix[:, comp] = 0
                self.helper_matrix[comp, comp] = 1

            # Convert excluded components set to a numpy array for consistency
            self.excluded_components = np.array(list(self.excluded_components))

