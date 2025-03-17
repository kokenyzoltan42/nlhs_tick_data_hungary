import numpy as np
import pandas as pd


class LogRatioVarianceCalculator:
    # TODO: A cikkben erre "variation matrix"-ként utalnak, de nem vagyok biztos benne, hogy az annyira jó megnevezés
    """
    A class to calculate the log-ratio variance (T matrix) of a set of variables from a DataFrame.
    The code assumes that the rows contain the samples and rows contain the OTUs.

    The log-ratio variance (referenced as T matrix on the Wiki page) is calculated by comparing the log of the ratio
    of each pair of OTUs across all samples. This measure captures the variability in the relationships between
    variables.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the LogRatioVarianceCalculator with a given DataFrame.

        :param data: A pandas DataFrame where each row represents a sample and each column represents an OTU.
        """
        self.data = data

        self.result: pd.DataFrame | None = None

    def run(self):
        """
        Runs the pipeline of the calculation of the log-ratio variance matrix (T).
        """
        self.calc_log_ratio_var()

    def calc_log_ratio_var(self):
        """
        Calculate the log-ratio variance for each pair of OTUs across all samples.

        This method computes the log of the ratio between every pair of variables (i, j) for each
        sample, and then calculates the variance of these log-ratios across all samples.

        The resulting variance matrix (T) represents the variability of the log-ratio between
        each pair of variables.
        """
        # Convert the DataFrame to a numpy array (of floats)
        variable_data = 1.0 * np.asarray(self.data)

        num_samples, num_otus = variable_data.shape

        # Create a 3D array where each element contains a copy of the variable_data along the 3rd dimension
        data_expanded = np.tile(variable_data.reshape((num_samples, num_otus, 1)), (1, 1, num_otus))

        # Transpose the data along the last two axes
        data_transposed = data_expanded.transpose(0, 2, 1)

        # Calculate the log of the ratio between every pair of variables (i, j) for each sample
        log_ratios = np.log(1.0 * data_expanded / data_transposed)

        # Compute the variance of the log-ratios for each OTUs
        self.result = log_ratios.var(axis=0, ddof=1)
