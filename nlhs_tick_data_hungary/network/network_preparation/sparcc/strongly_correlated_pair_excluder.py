from typing import Tuple

import numpy as np

from nlhs_tick_data_hungary.network.network_preparation.sparcc.basis_variance_calculator import BasisVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation.sparcc.correlation_calculator import CorrelationCalculator


class StronglyCorrelatedPairHandler:
    """
    Handles the identification and exclusion of strongly correlated pairs within a dataset.
    Iteratively removes the most correlated pairs until a defined exclusion threshold is met.
    """

    def __init__(self, variation_matrix: np.ndarray, correlations: np.ndarray, helper_matrix: np.ndarray,
                 exclusion_threshold: float, exclusion_iterations: int):
        """
        Initializes the handler with necessary matrices and exclusion parameters.

        :param np.ndarray variation_matrix: Matrix containing variance information.
        :param np.ndarray correlations: Precomputed correlation matrix.
        :param np.ndarray helper_matrix: Helper matrix to track modifications.
        :param float exclusion_threshold: Threshold above which correlations are considered too strong.
        :param int exclusion_iterations: Maximum number of exclusion iterations allowed.
        """
        self.variation_matrix = variation_matrix
        self.correlations = correlations
        self.helper_matrix = helper_matrix
        self.exclusion_threshold = exclusion_threshold
        self.exclusion_iterations = exclusion_iterations

        self.num_of_components = variation_matrix.shape[1]
        self.excluded_pairs = []  # List to store excluded pairs
        self.excluded_components = np.array([])  # Array to track components excluded due to excessive exclusions

    def run(self):
        """
        Iteratively finds and excludes strongly correlated pairs, updating the correlation matrix at each step.
        """
        for _ in range(self.exclusion_iterations):
            to_exclude = self.find_new_excluded_pair()
            if to_exclude is None:
                break  # Stop if no new pairs exceed the threshold

            self.excluded_pairs.append(to_exclude)
            i, j = to_exclude

            # Update the helper matrix to reflect exclusions
            self.helper_matrix[i, j] -= 1
            self.helper_matrix[j, i] -= 1
            self.helper_matrix[i, i] -= 1
            self.helper_matrix[j, j] -= 1

            # Set excluded pairs to zero in variation matrix
            inds = tuple(zip(*self.excluded_pairs))
            self.variation_matrix[inds] = 0
            self.variation_matrix.T[inds] = 0

            # Identify components that need exclusion
            self.exclude_components()

            # Recalculate correlation matrix using the updated variation matrix
            variance_calculator = BasisVarianceCalculator(log_ratio_variance=self.variation_matrix,
                                                          helper_matrix=self.helper_matrix)
            variance_calculator.run()
            basis_variances = variance_calculator.result

            correlation_calculator = CorrelationCalculator(log_ratio_variance=self.variation_matrix,
                                                           basis_variances=basis_variances)
            correlation_calculator.run()
            self.correlations = correlation_calculator.result

            # Mark excluded components in correlation matrix as NaN
            for excluded_component in self.excluded_components:
                self.correlations[excluded_component, :] = np.nan
                self.correlations[:, excluded_component] = np.nan

    def find_new_excluded_pair(self) -> Tuple[int, int] | None:
        """
        Identifies the most correlated pair in the dataset that has not yet been excluded.

        :return (Tuple[int, int] | None): A tuple (i, j) of indices representing the most correlated pair,
         or None if no pair exceeds the threshold.
        """
        # Consider only upper triangle of the correlation matrix for faster calculation
        corr_temp = np.triu(np.abs(self.correlations), 1)
        if self.excluded_pairs:
            corr_temp[tuple(zip(*self.excluded_pairs))] = 0  # Mask already excluded pairs

        # Find the most correlated pair
        i, j = np.unravel_index(np.argmax(corr_temp), corr_temp.shape)
        corr_max = corr_temp[i, j]

        # Return the pair if correlation exceeds the threshold, otherwise return None
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
            # Raise an error if too many components have been excluded
            if len(self.excluded_components) > (self.num_of_components - 4):
                raise ValueError("Too many components had to be excluded from the analysis")

            # Update matrices to reflect exclusions
            for comp in newly_excluded_components:
                self.variation_matrix[comp, :] = 0
                self.variation_matrix[:, comp] = 0
                self.helper_matrix[comp, :] = 0
                self.helper_matrix[:, comp] = 0
                self.helper_matrix[comp, comp] = 1  # Keep diagonal elements to maintain matrix structure

            # Convert excluded components set to a numpy array for consistency
            self.excluded_components = np.array(list(self.excluded_components))
