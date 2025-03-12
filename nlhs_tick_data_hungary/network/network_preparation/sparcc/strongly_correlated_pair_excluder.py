from typing import Tuple

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import CorrelationCalculator


class StronglyCorrelatedPairExcluder:
    # TODO: jobb név kell, mert előszöris fura, hogy ilyen nevű osztályt futtatunk a SparCCRunner-ben, másodszor pedig
    #  itt nem is vesszük ki az erősen korreláló párokat, csak a komponenseket (lehet fel kellene robbantani ezt
    #  az osztályt valahogy)
    """
    This class identifies and excludes highly correlated pairs of components (e.g., bacterial species)
    from a dataset based on a specified correlation threshold. The process iterates for a given number
    of times, updating a helper matrix that tracks exclusions and recomputing correlations after each iteration.
    """

    def __init__(self, data: pd.DataFrame, x_iter: int, threshold: float):
        """
        Initializes the excluder with the provided data, number of iterations, and correlation threshold.

        :param pd.DataFrame data: Resampled data
        :param int x_iter: Number of iterations for the exclusion process.
        :param float threshold: Correlation threshold above which pairs are excluded.
        """
        # Resampled data
        self.data = data
        # Number of times to run the iteration of excluding
        self.x_iter = x_iter
        # Above this threshold the most correlating pair is added to the list of excluded pairs
        self.threshold = threshold

        # Number of components (e.g., bacteria)
        self.num_of_components = self.data.shape[1]
        # Helper matrix (referred to as M in documentation) for tracking exclusions
        self.helper_matrix: (np.ndarray | None) = None
        # Copy of the firstly calculated variation matrix
        self.variation_matrix_copy = None
        # List that collects the most correlated pairs to be excluded
        self.excluded_pairs = []
        # List that collects components that have been entirely excluded from analysis
        self.excluded_components = np.array([])
        # Stores the final correlation results after exclusions
        self.result: (pd.DataFrame | None) = None

    def run(self):
        """
        Executes the iterative exclusion process by identifying highly correlated pairs, updating
        the helper matrix, and recomputing correlations.
        """
        # Initialize the helper matrix with predefined values
        self.helper_matrix = (np.ones((self.num_of_components, self.num_of_components)) +
                              np.diag([self.num_of_components - 2] * self.num_of_components))

        # Initial correlation calculation
        correlation_calculator = CorrelationCalculator(data=self.data,
                                                       helper_matrix=self.helper_matrix,
                                                       var_temp_copy=None)
        correlation_calculator.run()
        correlations = correlation_calculator.result
        self.variation_matrix_copy = correlation_calculator.variation_matrix

        for xi in range(self.x_iter):
            # Find the next most correlated pair to exclude
            to_exclude = self.find_new_excluded_pair(correlations=correlations,
                                                     threshold=self.threshold,
                                                     previously_excluded_pairs=self.excluded_pairs)
            if to_exclude is None:
                break  # Stop if no more pairs exceed the threshold

            self.excluded_pairs.append(to_exclude)
            i, j = to_exclude
            # Update the helper matrix to reflect exclusions
            self.helper_matrix[i, j] -= 1
            self.helper_matrix[j, i] -= 1
            self.helper_matrix[i, i] -= 1
            self.helper_matrix[j, j] -= 1

            # Exclude components (if necessary)
            self.exclude_components()

            # Recalculate correlations with the updated helper matrix
            another_correlation_calculator = CorrelationCalculator(data=self.data,
                                                                   helper_matrix=self.helper_matrix,
                                                                   var_temp_copy=self.variation_matrix_copy)
            another_correlation_calculator.run()
            correlations = another_correlation_calculator.result

            # Replace excluded components' correlations with NaN values
            for excluded_component in self.excluded_components:
                correlations[excluded_component, :] = np.nan
                correlations[:, excluded_component] = np.nan

        # Store the final correlation results
        self.result = correlations

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
