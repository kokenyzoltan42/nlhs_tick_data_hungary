import numpy as np

from nlhs_tick_data_hungary.network.network_preparation import BasisVarianceCalculator
from nlhs_tick_data_hungary.network.network_preparation import CorrelationCalculator


class CorrelationUpdater:
    """
    Manages the computation and updating of correlation matrices.
    This class handles the execution of BasisVarianceCalculator and CorrelationCalculator
    to ensure that correlation matrices are properly recalculated after exclusions.
    """

    @staticmethod
    def calculate_correlation(variation_matrix: np.ndarray, helper_matrix: np.ndarray) -> np.ndarray:
        """
        Computes the updated correlation matrix using the provided variation matrix and helper matrix.

        :param np.ndarray variation_matrix: An array containing the variation matrix
        :param np.ndarray helper_matrix: An array containing the helper matrix (also referenced as the $M$ matrix)
        :return np.ndarray: The updated correlation matrix.
        """
        variance_calculator = BasisVarianceCalculator(log_ratio_variance=variation_matrix, helper_matrix=helper_matrix)
        variance_calculator.run()
        basis_variances = variance_calculator.result

        correlation_calculator = CorrelationCalculator(log_ratio_variance=variation_matrix,
                                                       basis_variances=basis_variances)
        correlation_calculator.run()
        return correlation_calculator.result
