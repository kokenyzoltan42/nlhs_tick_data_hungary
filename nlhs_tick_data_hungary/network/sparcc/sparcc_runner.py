import os

import datetime
import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.network.sparcc.correlation_updater import CorrelationUpdater
from nlhs_tick_data_hungary.network.sparcc import LogRatioVarianceCalculator
from nlhs_tick_data_hungary.network.sparcc import SparCCResult
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
            self.output_dir = f"SparCC_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(self.output_dir, exist_ok=True)

    def run(self) -> SparCCResult:
        """
        Executes the SparCC correlation estimation algorithm over multiple iterations.

        Iteratively computes correlation matrices and delegates the saving of resampled data and correlation
        matrices to the SparCCResult class. The final median correlation matrix is also stored in the result object.

        :return object SparCCResult: Object containing the final result, and correlation matrices from every iteration
        and clr_run flags.
        """
        # Instantiate the result object
        result_obj = SparCCResult(args=self.args)

        # To collect correlation matrices from each iteration for computing the median later.
        correlation_results = []

        for iteration in range(self.args['n_iter']):
            self.estimate_component_fractions()

            iteration_dir = None
            if self.args["do_download_data"]:
                # Create iteration folder
                iteration_dir = os.path.join(self.output_dir, f"Iteration_{iteration}")
                os.makedirs(iteration_dir, exist_ok=True)
                # Saving resampled data in `SparCCResult`
                result_obj.save_resampled_data(iteration_dir=iteration_dir,
                                               resampled_data=self.data,
                                               columns=list(self.df.columns))

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
                initial_log_ratio_variance=None
            )

            # Iteratively remove strongly correlated pairs
            iterative_process = StronglyCorrelatedPairHandler(log_ratio_variances=log_ratio_variances,
                                                              correlations=correlations,
                                                              helper_matrix=helper_matrix,
                                                              exclusion_threshold=self.args['threshold'],
                                                              exclusion_iterations=self.args['x_iter'],
                                                              resampled_data=self.data)
            iterative_process.run()
            correlation_results.append(iterative_process.correlations)

            # Save iteration results (correlation matrix and clr flag) into result_obj
            result_obj.results[f"iteration_{iteration}"] = {
                "correlation_matrix": iterative_process.correlations,
                "clr_run": iterative_process.did_clr_run
            }


            if self.args["do_download_data"]:
                # Delegate saving of correlation matrix and clr_run flag to SparCCResult
                result_obj.save_iteration_data(iteration_dir=iteration_dir, iteration=iteration)

        # Compute the median correlation matrix across iterations and store it in result_obj
        result_obj.final_result = np.nanmedian(np.array(correlation_results), axis=0)

        # Return the result object containing final and per-iteration information
        return result_obj

    def estimate_component_fractions(self):
        """
        Resample the data using a Dirichlet distribution applied row-wise.

        Each row of the dataset is treated as a parameter vector for the Dirichlet distribution,
        generating new resampled compositions while preserving the compositional nature of the data.
        """
        self.data = np.apply_along_axis(
            lambda x: np.random.mtrand.dirichlet(x + 1),
            axis=0,
            arr=self.df
        )
