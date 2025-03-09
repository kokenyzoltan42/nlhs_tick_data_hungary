import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import BasisVarianceCalculator


class CorrelationCalculator:
    def __init__(self, data: pd.DataFrame, helper_matrix: np.ndarray, help_,
                 var_temp_copy):
        self.data = data
        self.helper_matrix = helper_matrix
        self.help_ = help_
        self.var_temp_copy = var_temp_copy

        self.var_temp = None

        self.result: (pd.DataFrame | None) = None

    def run(self):
        self.substitute_into_formula()
        # print('Korreláció \n', self.result[1, 0])

    def substitute_into_formula(self):
        basis_variance_calculator = BasisVarianceCalculator(data=self.data,
                                                            helper_matrix=self.helper_matrix,
                                                            help_=self.help_,
                                                            var_temp_copy=self.var_temp_copy)
        basis_variance_calculator.run()

        basis_variance = basis_variance_calculator.result
        self.var_temp = basis_variance_calculator.korr_hoz

        omega_i, omega_j = np.meshgrid(basis_variance, basis_variance)

        numerator = 0.5 * (omega_i + omega_j - self.var_temp)

        self.result = numerator / np.sqrt(omega_i) / np.sqrt(omega_j)
