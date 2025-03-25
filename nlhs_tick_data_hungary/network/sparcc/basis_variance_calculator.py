import numpy as np
import pandas as pd


class BasisVarianceCalculator:
    """
    A class for calculating the basis variances based on the log-ratio variances.
    """
    def __init__(self, log_ratio_variance: np.ndarray, helper_matrix: np.ndarray):
        """
       Initializes the basis variance calculator with input data, a helper matrix,
        and a copy of variances of log-ratios.

       :param np.ndarray log_ratio_variance: A matrix containing the log-ratio variances between OTUs.
       :param np.ndarray helper_matrix: A matrix used for tracking exclusions and modifications.
       """
        # Array containing the log-ratio variances (often referenced as variation matrix, or T matrix)
        self.log_ratio_variance = log_ratio_variance
        # Helper matrix (M)
        self.helper_matrix = helper_matrix

        # Attribute to store the basis variances
        self.result: (pd.DataFrame | None) = None

    def run(self):
        """
        This method runs the pipeline of the estimation of the basis variances.
        """
        self.calculate_basis_variance()

    def calculate_basis_variance(self):
        """
        Function to estimate the variances (referenced in the Wiki as the Omega matrix) from the ith(?) equation from
        the Wiki page with the following steps:

        We can estimate the basis variances if we can solve the following equation: Ax = b, where A is the helper
        matrix, x is the matrix containing the basis variances and b is the
        sum of columns of the log-ratio variances (t_i). We can solve the equation if we multiply the equation
        with the inverse of A from the left (x = M^{-1} \cdot b).
        """
        # Calculating the inverse of the helper matrix (M) with the Moore-Penrose inverse
        helper_matrix_inv = np.linalg.pinv(self.helper_matrix)
        # Multiplying the sum of the columns of the log-ratio variances with
        # the inverse of the helper matrix from the left
        self.result = np.dot(helper_matrix_inv, self.log_ratio_variance.sum(axis=1))

        # If any value is less than zero, replace it with a small number
        self.result[self.result <= 0] = 1e-6
