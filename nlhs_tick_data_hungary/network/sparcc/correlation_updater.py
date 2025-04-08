import numpy as np

from nlhs_tick_data_hungary.network.sparcc import BasisVarianceCalculator
from nlhs_tick_data_hungary.network.sparcc import CorrelationCalculator


class CorrelationUpdater:
    """
    Manages the computation and updating of correlation matrices.
    This class handles the execution of BasisVarianceCalculator and CorrelationCalculator
    to ensure that correlation matrices are properly recalculated after exclusions.
    """

    @staticmethod
    def calculate_correlation(newly_calculated_log_ratio_variances: np.ndarray, helper_matrix: np.ndarray,
                              original_log_ratio_variance: np.ndarray | None) -> np.ndarray:
        """
        Computes the updated correlation matrix using the provided log-ratio variances and helper matrix.

        :param np.ndarray newly_calculated_log_ratio_variances: An array containing the newly calculated
        log-ratio variances
        :param np.ndarray helper_matrix: An array containing the helper matrix (also referenced as the $M$ matrix)
        :param np.ndarray original_log_ratio_variance: An array containing the original (before the exclusion iteration)
         log-ratio variances
        :return np.ndarray: The updated correlation matrix.
        """
        variance_calculator = BasisVarianceCalculator(log_ratio_variance=newly_calculated_log_ratio_variances,
                                                      helper_matrix=helper_matrix)
        variance_calculator.run()
        basis_variances = variance_calculator.result

        # If we want to calculate the correlation before the exclusion process, then we only have one version of
        # log-ratio variances
        if original_log_ratio_variance is None:
            original_log_ratio_variance = newly_calculated_log_ratio_variances.copy()
        # For the calculation of the correlation we need the "original", firstly calculated log-ratio variances
        # Because the flow chart in the original documentation says that after each iteration we only
        # recalculate the "component variations" (sum of the columns in the variation matrix)
        correlation_calculator = CorrelationCalculator(log_ratio_variance=original_log_ratio_variance,
                                                       basis_variances=basis_variances)
        correlation_calculator.run()
        return correlation_calculator.result
