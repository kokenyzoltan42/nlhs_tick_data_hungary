import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import BasisVarianceCalculator


class CorrelationCalculator:
    """
    This class computes correlation values based on log-ratio variances and estimated basis variances.
    """

    def __init__(self, data: pd.DataFrame, helper_matrix: np.ndarray, var_temp_copy: np.ndarray | None):
        """
        Initializes the correlation calculator with input data, a helper matrix, and a variation matrix copy.

        :param pd.DataFrame data: Resampled data
        :param np.ndarray helper_matrix: A matrix used for tracking exclusions and modifications.
        :param (np.ndarray | None) var_temp_copy: A copy of the variation matrix (if it has been calculated
        previously) used in calculations.
        """
        # Resampled data
        self.data = data
        # Helper matrix (M)
        self.helper_matrix = helper_matrix
        # Copy of the calculated variation matrix (T)
        self.var_temp_copy = var_temp_copy
        # Log-ratio variance matrix, used for correlation calculations
        self.variation_matrix = None
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
        # Compute basis variances and log-ratio variances
        basis_variance_calculator = BasisVarianceCalculator(data=self.data,
                                                            helper_matrix=self.helper_matrix,
                                                            var_temp_copy=self.var_temp_copy)
        basis_variance_calculator.run()

        # Store computed variances
        basis_variance = basis_variance_calculator.result
        self.variation_matrix = basis_variance_calculator.log_ratio_variance

        # Create a meshgrid for basis variances
        omega_i, omega_j = np.meshgrid(basis_variance, basis_variance)
        # Calculating the numerator (basis covariance(?))
        numerator = 0.5 * (omega_i + omega_j - self.var_temp)
        # Storing correlations
        numerator = 0.5 * (omega_i + omega_j - self.variation_matrix)
        # Compute and store the correlation matrix
        self.result = numerator / np.sqrt(omega_i) / np.sqrt(omega_j)
