from typing import Tuple

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import CorrelationCalculator


class StronglyCorrelatedPairExcluder:
    def __init__(self, data: pd.DataFrame, x_iter: int, threshold: float):
        self.data = data
        self.x_iter = x_iter
        self.threshold = threshold

        self.num_of_components = self.data.shape[0]
        self.helper_matrix: (np.ndarray | None) = None
        self.excluded_pairs = []
        self.excluded_components = np.array([])

        self.result: (pd.DataFrame | None) = None

    def run(self):
        # In the diagonal it has the number of total OTUs - 1, every other element is 1
        self.helper_matrix = np.ones((self.num_of_components, self.num_of_components)) + \
                        np.diag([self.num_of_components - 2] * self.num_of_components)

        correlation_calculator = CorrelationCalculator(data=self.data,
                                                       helper_matrix=self.helper_matrix)
        correlation_calculator.run()
        correlations = correlation_calculator.result

        for xi in range(self.x_iter):
            to_exclude = self.find_new_excluded_pair(correlations=correlations,
                                                     threshold=self.threshold,
                                                     previously_excluded_pairs=self.excluded_pairs)
            if to_exclude is None:
                break

            self.excluded_pairs.append(to_exclude)
            i, j = to_exclude
            self.helper_matrix[i, j] -= 1
            self.helper_matrix[j, i] -= 1
            self.helper_matrix[i, i] -= 1
            self.helper_matrix[j, j] -= 1

            # TODO: itt elvileg le kellene nullázni T-ben is ezeket az indexeket, de szerintem nem szükséges (gondold végig)
            self.exclude_components()

            another_correlation_calculator = CorrelationCalculator(data=self.data,
                                                                   helper_matrix=self.helper_matrix)
            another_correlation_calculator.run()
            correlations = another_correlation_calculator.result
            for excluded_component in self.excluded_components:
                correlations[excluded_component, :] = np.nan
                correlations[:, excluded_component] = np.nan

        self.result = correlations

    @staticmethod
    def find_new_excluded_pair(correlations: np.ndarray,
                               threshold: float,
                               previously_excluded_pairs: list) -> Tuple[int, int] | None:
        # Only working in the upper triangle (excluding diagonal)
        corr_temp = np.triu(abs(correlations), 1)

        corr_temp[tuple(zip(*previously_excluded_pairs))] = 0

        # Finding the most correlated pair
        i, j = np.unravel_index(np.argmax(corr_temp), corr_temp.shape)
        corr_max = corr_temp[i, j]

        if corr_max > threshold:
            return i, j
        else:
            return None

    def exclude_components(self):
        # Searching for new components to exclude
        num_of_excluded = np.bincount(np.ravel(self.excluded_pairs))
        previously_excluded_components = set(self.excluded_components.copy())
        excluded_components = np.where(num_of_excluded >= self.num_of_components - 3)[0]
        newly_excluded_components = set(excluded_components) - previously_excluded_components

        if len(newly_excluded_components) > 0:
            if len(excluded_components) > (self.num_of_components - 4):
                raise ValueError("Túl sok komponenst kellett kihagyni az elemzésből")
                # TODO: ilyenkor máshol clr-t alkalmaznak és azzal térnek vissza, lehet itt is azt kellene
                #  és ValueError helyett csak egy warning-ot kiírni
            for excluded_component in newly_excluded_components:
                self.helper_matrix[excluded_component, :] = 0
                self.helper_matrix[:, excluded_component] = 0
                self.helper_matrix[excluded_component:excluded_component] = 0
