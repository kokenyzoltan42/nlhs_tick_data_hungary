import numpy as np
import pandas as pd


class CorrelationCalculator:
    """
    This class computes correlation values based on log-ratio variances and estimated basis variances.
    """

    def __init__(self, log_ratio_variance: np.ndarray, basis_variances: np.ndarray):
        """
        Initializes the correlation calculator with input data, a helper matrix, and a variation matrix copy.

        :param np.ndarray log_ratio_variance: A matrix containing log-ratio variances for each OTU
        :param np.ndarray basis_variances: A matrix containing basis variances for each OTU
        """
        # Array containing the log-ratio variances (Variation matrix, also referenced as T matrix)
        self.log_ratio_variance = log_ratio_variance
        # Array containing the basis variances
        self.basis_variances = basis_variances
        # Attribute to store correlation results
        self.result: (pd.DataFrame | None) = None

    def run(self):
        """
        Executes the correlation calculation process by calling the formula substitution method.
        """
        self.substitute_into_formula()

    def substitute_into_formula(self):
        """
        Computes correlation values using basis variances and log-ratio variances.

        This method initializes and runs the `BasisVarianceCalculator` to obtain basis variances and the variation
        matrix. The obtained values are then substituted into the appropriate formula to compute correlations.
        """
        # Create a meshgrid for basis variances
        omega_i, omega_j = np.meshgrid(self.basis_variances, self.basis_variances)
        # Storing correlations
        numerator = 0.5 * (omega_i + omega_j - self.log_ratio_variance)
        # Compute and store the correlation matrix
        self.result = numerator / np.sqrt(omega_i) / np.sqrt(omega_j)
