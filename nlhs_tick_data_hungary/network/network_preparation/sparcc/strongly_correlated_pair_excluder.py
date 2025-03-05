from typing import Tuple

import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc.correlation_calculator import CorrelationCalculator


class StronglyCorrelatedPairExcluder:
    def __init__(self, data: pd.DataFrame, x_iter: int, tol: float = 0.1):
        self.data = data
        self.x_iter = x_iter
        self.tol = tol

        self.result: (pd.DataFrame | None) = None

    def run(self):
        num_of_components = self.data.shape[0]

        # In the diagonal it has the number of total OTUs - 1, every other element is 1
        helper_matrix = np.ones((num_of_components, num_of_components)) + np.diag([num_of_components - 2] * num_of_components)

        correlation_calculator = CorrelationCalculator(data=self.data,
                                                       helper_matrix=helper_matrix)
        correlation_calculator.run()
        correlations = correlation_calculator.result

        excluded_pairs = []
        excluded_components = np.array([])

        for xi in range(self.x_iter):
            to_exclude = self.find_new_excluded_pair(correaltions=correlations,
                                                     tol=self.tol,
                                                     previously_excluded_pairs=excluded_pairs)
            if to_exclude is None:
                break

            excluded_pairs.append(to_exclude)
            i, j = to_exclude
            helper_matrix[i, j] -= 1
            helper_matrix[j, i] -= 1
            helper_matrix[i, i] -= 1
            helper_matrix[j, j] -= 1

            # TODO: itt elvileg le kellene nullázni T-ben is ezeket az indexeket, de szerintem nem szükséges (gondold végig)
            self.exclude_components()

            another_correlation_calculator = CorrelationCalculator(data=self.data,
                                                                   helper_matrix=helper_matrix)
            # TODO: stb. és utána a kivett komponensek helyein át kell írni mindent nan-ra
            # TODO: ne felejtsd el az eredméyneket self.result-ba menteni

    @staticmethod
    def find_new_excluded_pair(correlations: np.array,  # TODO: ezt megnézni, hogy helyes-e
                               tol: float,
                               previously_excluded_pairs: list) -> Tuple[int, int] | None:
        # Only working in the upper triangle (excluding diagonal)
        corr_temp = np.triu(abs(correlations), 1)

        corr_temp[zip(*previously_excluded_pairs)] = 0

        # Finding the most correlated pair
        i, j = np.unravel_index(np.argmax(corr_temp), corr_temp.shape)
        corr_max = corr_temp[i, j]

        if corr_max > tol:
            return i, j
        else:
            return None

    @staticmethod
    def exclude_components(excluded_pairs: list,
                           excluded_components: np.ndarray,
                           num_of_components: int,
                           helper_matrix: np.ndarray):
        # Searching for new components to exclude
        # TODO: zavaró ez a sok hasonló nevű változó
        num_of_excluded = np.bincount(np.ravel(excluded_pairs))
        previously_excluded_components = set(excluded_components.copy())
        excluded_components = np.where(num_of_excluded >= num_of_components - 3)[0]
        newly_excluded_components = set(excluded_components) - previously_excluded_components

        if len(newly_excluded_components) > 0:
            if len(excluded_components) > (num_of_components - 4):
                raise ValueError("Túl sok komponenst kellett kihagyni az elemzésből")
                # TODO: itt máshol clr-t alkalmaznak és azzal térnek vissza, lehet itt is azt kellene
                #  és ValueError helyett csak egy warning-ot kiírni
            for excluded_component in newly_excluded_components:
                # TODO: túl hosszú ez a név szerintem
                # TODO: ennyi változó után lehet érdemesebb lenne tagváltozókat használni
                helper_matrix[excluded_component, :] = 0
                helper_matrix[:, excluded_component] = 0
                helper_matrix[excluded_component:excluded_component] = 0


                # TODO: JAjjjj !!! EZ ÍGY ROSSZ, NE LEGYEN STATIKUS, ENNEK NYÍLVÁN TAGFÜGGVÉNYNEK KELL LENNIE
                #  MINDEN, AMI ITT ARGUMENTUM, AZ LEGYEN TAGVÁLTOZÓ