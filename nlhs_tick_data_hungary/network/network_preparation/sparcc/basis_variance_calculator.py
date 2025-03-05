import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import LogRatioVarianceCalculator


class BasisVarianceCalculator:
    def __init__(self, data: pd.DataFrame, helper_matrix: np.ndarray):  # lehet pandas a helper_matrix
        self.data = data
        self.helper_matrix = helper_matrix

        self.log_ratio_variance: (np.ndarray | None) = None

        self.result: (pd.DataFrame | None) = None

    # TODO: log-ratio var importját rövidíteni

    def run(self):
        self.calculate_basis_variance()

    def calculate_basis_variance(self):
        log_ratio_variance_calculator = LogRatioVarianceCalculator(data=self.data)
        log_ratio_variance_calculator.run()

        self.log_ratio_variance = log_ratio_variance_calculator.result

        helper_matrix_inv = np.linalg.inv(self.helper_matrix)

        self.result = np.dot(helper_matrix_inv, self.log_ratio_variance.sum(axis=1))

        self.result[self.result <= 0] = 1e-6
