import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import LogRatioVarianceCalculator


class BasisVarianceCalculator:
    def __init__(self, data: pd.DataFrame, helper_matrix: np.ndarray, help_,
                 var_temp_copy):
        self.data = data
        self.helper_matrix = helper_matrix
        self.help_ = help_
        self.var_temp_copy = var_temp_copy


        self.korr_hoz = None

        self.log_ratio_variance: (np.ndarray | None) = None

        self.result: (pd.DataFrame | None) = None

    def run(self):
        self.calculate_basis_variance()

    def calculate_basis_variance(self):
        if self.var_temp_copy is None:
            log_ratio_variance_calculator = LogRatioVarianceCalculator(data=self.data)
            log_ratio_variance_calculator.run()
            self.log_ratio_variance = log_ratio_variance_calculator.result
        else:
            self.log_ratio_variance = self.var_temp_copy

        self.korr_hoz = self.log_ratio_variance

        #if self.help_ is not None:
        #    self.log_ratio_variance[self.help_] = 0
        #    self.log_ratio_variance.T[self.help_] = 0

        #helper_matrix_inv = np.linalg.pinv(self.helper_matrix)

        #self.result = np.dot(helper_matrix_inv, self.log_ratio_variance.sum(axis=1))
        helper_matrix_inv = np.linalg.pinv(self.helper_matrix)
        self.result = np.dot(helper_matrix_inv, self.log_ratio_variance.sum(axis=1))

        self.result[self.result < 0] = 1e-6
