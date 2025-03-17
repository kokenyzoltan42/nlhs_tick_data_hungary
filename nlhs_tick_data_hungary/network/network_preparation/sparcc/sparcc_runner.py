from typing import Tuple

import numpy as np
import pandas as pd

# TODO: ezeke menjenek az __init__-be?
from nlhs_tick_data_hungary.network.network_preparation.sparcc.basis_variance_calculator import BasisVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.correlation_calculator import CorrelationCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.log_ratio_variance_calculator import LogRatioVarianceCalculator


class SparCCRunner:
    def __init__(self, data: pd.DataFrame, args: dict):
        self.data = data
        self.args = args

        self.num_of_components = self.data.shape[1]
        self.helper_matrix = None

        self.correlations = None

        self.excluded_pairs = None
        self.excluded_components = None

        self.result = None

    # TODO: először úgy implementáld, hogy az excludion is ide kerüljön, utána gondolkozz azon, hogyan lehet külön osztály

    def run(self) -> pd.DataFrame:

        correlations = []

        for _ in range(self.args['n_iter']):
            self.estimate_component_fractions()
            result = self.calc_correlations_with_sparcc()
            correlations.append(result)

        return np.nanmedian(np.array(correlations), axis=0)

    def estimate_component_fractions(self):
        """
        Resample the data using a Dirichlet distribution applied row-wise.

        Each row of the data is treated as the parameters for the Dirichlet distribution,
        which generates(?) a new row of samples based on those parameters.
        """
        self.data = np.apply_along_axis(
            lambda x: np.random.mtrand.dirichlet(x + 1),
            axis=1,
            arr=self.data
        )

    @staticmethod
    def find_new_excluded_pair(correlations: np.ndarray,
                               threshold: float,
                               previously_excluded_pairs: list) -> Tuple[int, int] | None:
        """
        Identifies the most correlated pair in the dataset that has not yet been excluded.

        :param np.ndarray correlations: A 2D array containing correlation values.
        :param float threshold: The threshold above which a pair will be excluded.
        :param list previously_excluded_pairs: A list of previously excluded pairs to avoid "re-exclusion".
        :return Tuple[int, int] | None: The indices of the most correlated pair or None if no such pair exists.
        """
        # Consider only the upper triangle of the correlation matrix (excluding diagonal)
        corr_temp = np.triu(np.abs(correlations), 1)
        if previously_excluded_pairs:
            corr_temp[tuple(zip(*previously_excluded_pairs))] = 0  # Exclude already removed pairs

        # Find the most correlated pair
        i, j = np.unravel_index(np.argmax(corr_temp), corr_temp.shape)
        corr_max = corr_temp[i, j]

        # Return the pair if it exceeds the threshold, otherwise return None
        return (i, j) if corr_max > threshold else None

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
                self.variation_matrix_copy[comp, :] = 0
                self.variation_matrix_copy[:, comp] = 0
                self.helper_matrix[comp, :] = 0
                self.helper_matrix[:, comp] = 0
                self.helper_matrix[comp, comp] = 1

            # Convert excluded components set to a numpy array for consistency
            self.excluded_components = np.array(list(self.excluded_components))

    def calc_correlations_with_sparcc(self):

        self.helper_matrix = (np.ones((self.num_of_components, self.num_of_components)) +
                              np.diag([self.num_of_components - 2] * self.num_of_components))

        log_ratio_variances = LogRatioVarianceCalculator(data=self.data)
        log_ratio_variances.run()
        variation_matrix = log_ratio_variances.result
        basis_variances = BasisVarianceCalculator(log_ratio_variance=variation_matrix,
                                                  helper_matrix=self.helper_matrix)
        basis_variances.run()
        correlation_calculator = CorrelationCalculator(basis_variances=basis_variances.result,
                                                       log_ratio_variance=variation_matrix,
                                                       helper_matrix=self.helper_matrix)
        correlation_calculator.run()
        correlations = correlation_calculator.result

        for _ in range(self.args['x_iter']):
            to_exclude = self.find_new_excluded_pair(correlations=correlations,
                                                     threshold=self.args['threshold'],
                                                     previously_excluded_pairs=self.excluded_pairs)
            if to_exclude is None:
                break

            self.excluded_pairs.append(to_exclude)
            i, j = to_exclude

            self.helper_matrix[i, j] -= 1
            self.helper_matrix[j, i] -= 1
            self.helper_matrix[i, i] -= 1
            self.helper_matrix[j, j] -= 1

            # TODO: biztos szükség van transzponálásra?
            inda, indb = np.transpose(self.excluded_pairs)
            variation_matrix[inda, indb] = 0
            variation_matrix.T[inda, indb] = 0

            self.exclude_components()

            another_basis_variance_calculator = BasisVarianceCalculator(log_ratio_variance=variation_matrix,
                                                                        helper_matrix=self.helper_matrix)
            another_basis_variance_calculator.run()
            basis_variances = another_basis_variance_calculator.result
            another_correlation_calculator = CorrelationCalculator(log_ratio_variance=log_ratio_variances.result,
                                                                   basis_variances=basis_variances)
            another_correlation_calculator.run()
            correlations = another_correlation_calculator.result

            for excluded_component in self.excluded_components:
                correlations[excluded_component, :] = np.nan
                correlations[:, excluded_component] = np.nan

        self.result = correlations
