import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.network_preparation.sparcc import BasisVarianceCalculator


class CorrelationCalculator:
    def __init__(self, data: pd.DataFrame, helper_matrix: np.ndarray, var_temp_copy):
        # Resampled data
        self.data = data
        # Helper matrix (M)
        self.helper_matrix = helper_matrix
        # Copy of the calculated variation matrix (T)
        self.var_temp_copy = var_temp_copy
        # This attribute is going to contain the log-ratio variance. It is an attribute in order to access the log ratio
        # variance in the `StronglyCorrelatedPairExcluder`
        self.var_temp = None
        # Attribute to store results in
        self.result: (pd.DataFrame | None) = None

    def run(self):
        """
        Method for running the pipeline of the calculation of the correlations.
        """
        self.substitute_into_formula()

    def substitute_into_formula(self):
        """
        Method for calculating correlations.
        This method gets the basis variances and the variation matrix via the initiation
        and running of the `BasisVarianceCalculator`. After that we simply substitute into the ith(?) formula found
        in the Wiki page.
        """
        # Calculating basis variances and log-ratio variances
        basis_variance_calculator = BasisVarianceCalculator(data=self.data,
                                                            helper_matrix=self.helper_matrix,
                                                            var_temp_copy=self.var_temp_copy)
        basis_variance_calculator.run()
        # Storing results
        basis_variance = basis_variance_calculator.result
        self.var_temp = basis_variance_calculator.log_ratio_variance

        omega_i, omega_j = np.meshgrid(basis_variance, basis_variance)
        # Calculating the numerator (basis covariance(?))
        numerator = 0.5 * (omega_i + omega_j - self.var_temp)
        # Storing correlations
        self.result = numerator / np.sqrt(omega_i) / np.sqrt(omega_j)
