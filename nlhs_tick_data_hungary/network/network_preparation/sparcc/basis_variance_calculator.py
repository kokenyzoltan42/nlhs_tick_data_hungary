import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import LogRatioVarianceCalculator


class BasisVarianceCalculator:
    def __init__(self, data: pd.DataFrame, helper_matrix: np.ndarray,
                 var_temp_copy):
        # Resampled data
        self.data = data
        # Helper matrix (M)
        self.helper_matrix = helper_matrix
        # Copy of the variation matrix
        self.var_temp_copy = var_temp_copy

        # Variation matrix (T)
        self.log_ratio_variance: (np.ndarray | None) = None
        # Attribute store the basis variances
        self.result: (pd.DataFrame | None) = None

    def run(self):
        """
        This method runs the pipeline of the estimaton of the basis variances.
        """
        self.calculate_basis_variance()

    def calculate_basis_variance(self):
        """
        Function to estimate the variances (referenced in the Wiki as the Omega matrix) from the ith(?) equation from
        the Wiki page with the following steps:

        We can estimate the basis variances if we can solve the following equation: Ax = b, where A is the helper
        matrix, x is the matrix containing the variances and b is the of columns of the variation matrix (t_i).
        We can solve the equation if we multiply the equation with the inverse of A from the left (x = b \cdot M^{-1}).
        """
        if self.var_temp_copy is None:
            # If the variation matrix has not been calculated, then calculate it
            log_ratio_variance_calculator = LogRatioVarianceCalculator(data=self.data)
            log_ratio_variance_calculator.run()
            self.log_ratio_variance = log_ratio_variance_calculator.result
        else:
            self.log_ratio_variance = self.var_temp_copy

        # Calculating the inverse of the helper matrix (M) with the Moore-Penrose inverse
        helper_matrix_inv = np.linalg.pinv(self.helper_matrix)
        # Multiplying the sum of the columns of the variation matrix with
        # the inverse of the helper matrix from the left
        self.result = np.dot(helper_matrix_inv, self.log_ratio_variance.sum(axis=1))

        # If any value is less than zero, replace it with a small number
        self.result[self.result <= 0] = 1e-6
