import os
import numpy as np
import pandas as pd


class SparCCResult:
    """
    A container class for storing the results from executing the SparCC algorithm.

    This class holds the per-iteration results (correlation matrix and a bool value to indicate if the result is from
    the calculation of clr) in a dictionary, as well as the final median correlation matrix computed over
    all iterations. It also provides methods for saving both the resampled data and the per-iteration results in files.
    """
    def __init__(self, args: dict):
        """
        Initializes the SparCCResult instance.

        :param dict args: A dictionary of arguments including the number of iterations.
        """
        self.args = args

        # Stores iteration-specific results in a dictionary.
        self.results = {
            f'iteration_{iteration}': {"correlation_matrix": None, "clr_run": False}
            for iteration in range(self.args['n_iter'])
        }
        self.final_result = None  # The final median correlation matrix.

    def save_iteration_data(self, iteration_dir: str, iteration: int):
        """
        Saves the iteration results to the filesystem.

        Two files are produced: a CSV file for the correlation matrix and a text file for the clr_run flag.

        :param str iteration_dir: The directory where the files will be saved.
        :param int iteration: The current iteration number.
        """
        iteration_key = f"iteration_{iteration}"
        iter_result = self.results.get(iteration_key, {})

        # Save the correlation matrix as CSV if available.
        correlation_matrix = iter_result.get("correlation_matrix")
        if correlation_matrix is not None:
            df_correlation = pd.DataFrame(correlation_matrix)
            df_correlation.to_csv(os.path.join(iteration_dir, "correlation_matrix.csv"), index=False)

    @staticmethod
    def save_resampled_data(iteration_dir: str, resampled_data: np.ndarray, columns: list):
        """
        Saves the resampled data to the filesystem.

        Generates a CSV file from the resampled data using the provided column names.

        :param str iteration_dir: The directory where the data should be saved.
        :param np.ndarray resampled_data: The numpy array containing the resampled data.
        :param list columns: List or index of column names to use for the CSV file.
        """
        df_resampled = pd.DataFrame(resampled_data, columns=columns)
        df_resampled.to_csv(os.path.join(iteration_dir, "resampled_data.csv"), index=False)
