import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc.basis_variance_calculator import BasisVarianceCalculator


class CorrelationCalculator:
    def __init__(self, data: pd.DataFrame, helper_matrix: np.ndarray):
        self.data = data
        self.helper_matrix = helper_matrix

        self.result: (pd.DataFrame | None) = None

        # TODO: change implementation diagram description

    def run(self):
        self.substitute_into_formula()

    def substitute_into_formula(self):
        basis_variance_calculator = BasisVarianceCalculator(data=self.data,
                                                            helper_matrix=self.helper_matrix)
        basis_variance_calculator.run()

        basis_variance = basis_variance_calculator.result
        log_ratio_variance = basis_variance_calculator.log_ratio_variance

        omega_i, omega_j = np.meshgrid(basis_variance, basis_variance)

        numerator = 0.5 * (omega_i + omega_j - log_ratio_variance)

        self.result = numerator / np.sqrt(omega_i) / np.sqrt(omega_j)
