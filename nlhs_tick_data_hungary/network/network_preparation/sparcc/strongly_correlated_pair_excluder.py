from typing import Tuple

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import CorrelationCalculator


class StronglyCorrelatedPairExcluder:
    def __init__(self, data: pd.DataFrame, x_iter: int, threshold: float):
        # Resampled data
        self.data = data
        # Number of times to run the iteration of excluding
        self.x_iter = x_iter
        # Above this threshold the most correlating pair added to the list of excluded pairs
        self.threshold = threshold

        # Number of components (bacteria)
        self.num_of_components = self.data.shape[1]
        # This matrix is referred in the Wiki as M
        self.helper_matrix: (np.ndarray | None) = None
        # List that collects the most correlated pairs
        self.excluded_pairs = []
        # List that collects components that have been excluded from the analysis
        self.excluded_components = np.array([])

        # Attribute to save the correlation after the iteration
        self.result: (pd.DataFrame | None) = None

    def run(self):
        # In the diagonal it has the number of total OTUs - 1, every other element is 1
        self.helper_matrix = np.ones((self.num_of_components, self.num_of_components)) + \
                        np.diag([self.num_of_components - 2] * self.num_of_components)

        correlation_calculator = CorrelationCalculator(data=self.data,
                                                       helper_matrix=self.helper_matrix,
                                                       var_temp_copy=None)
        # Calculating (initial) correlations
        correlation_calculator.run()
        correlations = correlation_calculator.result
        var_temp_copy = correlation_calculator.var_temp

        for xi in range(self.x_iter):
            to_exclude = self.find_new_excluded_pair(correlations=correlations,
                                                     threshold=self.threshold,
                                                     previously_excluded_pairs=self.excluded_pairs)
            if to_exclude is None:
                print('\n\nÜdv\n\n', xi)
                break

            self.excluded_pairs.append(to_exclude)
            i, j = to_exclude
            self.helper_matrix[i, j] -= 1
            self.helper_matrix[j, i] -= 1
            self.helper_matrix[i, i] -= 1
            self.helper_matrix[j, j] -= 1

            self.exclude_components()

            #inda, indb = np.transpose(self.excluded_pairs)
            #inds = zip(*self.excluded_pairs)
            #inds = tuple(zip(*self.excluded_pairs))

            another_correlation_calculator = CorrelationCalculator(data=self.data,
                                                                   helper_matrix=self.helper_matrix,
                                                                   var_temp_copy=var_temp_copy)
            another_correlation_calculator.run()
            correlations = another_correlation_calculator.result
            for excluded_component in self.excluded_components:
                print('\n\nHali\n\n')
                correlations[excluded_component, :] = np.nan
                correlations[:, excluded_component] = np.nan

        self.result = correlations

    @staticmethod
    def find_new_excluded_pair(correlations: np.ndarray,
                               threshold: float,
                               previously_excluded_pairs: list) -> Tuple[int, int] | None:
        # Only working in the upper triangle (excluding diagonal)
        corr_temp = np.triu(np.abs(correlations), 1)
        if len(previously_excluded_pairs) > 0:
            corr_temp[tuple(zip(*previously_excluded_pairs))] = 0

        # Finding the most correlated pair
        i, j = np.unravel_index(np.argmax(corr_temp), corr_temp.shape)
        corr_max = corr_temp[i, j]
        if corr_max > threshold:
            return i, j
        else:
            return None

    def exclude_components(self):
        # Kiszámolja, mely komponenseket kell kizárni
        num_of_excluded = np.bincount(np.ravel(self.excluded_pairs))
        previously_excluded_components = set(self.excluded_components.copy())
        self.excluded_components = set(np.where(num_of_excluded >= self.num_of_components - 3)[0])
        newly_excluded_components = self.excluded_components - previously_excluded_components

        if newly_excluded_components:
            print('\n\nHelló\n\n')
            if len(self.excluded_components) > (self.num_of_components - 4):
                raise ValueError("Túl sok komponenst kellett kihagyni az elemzésből")
                # TODO: implement clr?
            for comp in newly_excluded_components:
                self.helper_matrix[comp, :] = 0
                self.helper_matrix[:, comp] = 0
                self.helper_matrix[comp, comp] = 1  # megfelelő nullázás
            # Frissítés: új kizárt komponensek hozzáadása
            self.excluded_components = np.array(list(self.excluded_components))
