import os

import datetime
import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.sparcc.correlation_updater import CorrelationUpdater
from nlhs_tick_data_hungary.network.sparcc import LogRatioVarianceCalculator
from nlhs_tick_data_hungary.network.sparcc import StronglyCorrelatedPairHandler


class SparCCRunner:
    """
    Executes the SparCC algorithm on input data, iteratively estimating correlation matrices.
    Handles resampling, variance computation, and iterative correlation exclusion.
    """

    def __init__(self, df: pd.DataFrame, args: dict):
        """
        Initializes the SparCCRunner with data and algorithm parameters.

        :param pd.DataFrame df: Input dataframe containing compositional data.
        :param dict args: Dictionary of parameters controlling the number of iterations, threshold, and exclusions.
        """
        # Original data
        self.df = df
        self.args = args

        # Attribute to store resampled data
        self.data = None

        # Create output directory if saving is enabled
        if self.args["do_download_data"]:
            self.output_dir = f"sparcc_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(self.output_dir, exist_ok=True)

    def run(self) -> np.ndarray:
        """
        Executes the SparCC correlation estimation algorithm over multiple iterations.

        :return np.ndarray: Median correlation matrix computed over all iterations.
        """
        correlation_results = []

        for iteration in range(self.args['n_iter']):
            self.estimate_component_fractions()

            # Saving resampled data
            if self.args["do_download_data"]:
                iteration_dir = os.path.join(self.output_dir, f"iteration_{iteration}")
                os.makedirs(iteration_dir, exist_ok=True)
                self.save_resampled_data(iteration_dir)

            # Compute log-ratio variances
            log_ratio_variances = LogRatioVarianceCalculator(data=self.data)
            log_ratio_variances.run()
            log_ratio_variances = log_ratio_variances.result.copy()
            num_of_components = log_ratio_variances.shape[1]

            # Initialize helper matrix for variance calculations
            helper_matrix = (np.ones((num_of_components, num_of_components)) +
                             np.diag([num_of_components - 2] * num_of_components))

            # Compute correlations
            correlations = CorrelationUpdater.calculate_correlation(
                newly_calculated_log_ratio_variances=log_ratio_variances,
                helper_matrix=helper_matrix,
                original_log_ratio_variance=None
            )

            # Iteratively remove strongly correlated pairs
            iterative_process = StronglyCorrelatedPairHandler(log_ratio_variances=log_ratio_variances,
                                                              correlations=correlations,
                                                              helper_matrix=helper_matrix,
                                                              exclusion_threshold=self.args['threshold'],
                                                              exclusion_iterations=self.args['x_iter'])

            iterative_process.run()
            correlation_results.append(iterative_process.correlations)

            # Saving correlations
            if self.args["do_download_data"]:
                self.save_correlation_matrix(iteration_dir, correlations)

        # Compute the median correlation matrix across iterations
        return np.nanmedian(np.array(correlation_results), axis=0)

    def estimate_component_fractions(self):
        """
        Resample the data using a Dirichlet distribution applied row-wise.

        Each row of the dataset is treated as a parameter vector for the Dirichlet distribution,
        generating new resampled compositions while preserving the compositional nature of the data.
        """
        self.data = np.apply_along_axis(
            lambda x: np.random.mtrand.dirichlet(x + 1),
            axis=1,
            arr=self.df
        )

    def save_resampled_data(self, iteration_dir: str):
        """
        Saves the resampled data to the specified iteration folder.

        :param str iteration_dir: The directory where the data should be saved.
        """
        df_resampled = pd.DataFrame(self.data, columns=self.df.columns)
        df_resampled.to_csv(os.path.join(iteration_dir, "resampled_data.csv"), index=False)

    @staticmethod
    def save_correlation_matrix(iteration_dir: str, correlation_matrix: np.ndarray):
        """
        Saves the correlation matrix to the specified iteration folder.

        :param str iteration_dir: The directory where the matrix should be saved.
        :param np.ndarray correlation_matrix: The computed correlation matrix.
        """
        df_correlation = pd.DataFrame(correlation_matrix)
        df_correlation.to_csv(os.path.join(iteration_dir, "correlation_matrix.csv"), index=False)
