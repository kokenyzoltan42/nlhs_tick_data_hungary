import numpy as np


class CLRCalculator:
    """
    A class to perform Centered Log-Ratio (CLR) transformation and compute correlation coefficients.
    """

    def __init__(self, data: np.ndarray):
        """
        Initializes the CLRCalculator with the given data.

        :param np.ndarray data (np.ndarray): A NumPy array containing the input data.
        """
        self.data = data.T

    def run(self) -> np.ndarray:
        """
        Executes the CLR transformation and computes correlations

        :return np.ndarray: Correlation matrix of CLR-transformed data.
        """
        return self.run_clr()

    def run_clr(self) -> np.ndarray:
        """
        Computes the CLR transformation and calculates the correlation matrix.

        :return np.ndarray: Correlation matrix of CLR-transformed data.
        """
        z = self.clr()

        # Compute correlation coefficients from the CLR-transformed data
        correlations = np.corrcoef(z)

        return correlations

    def clr(self) -> np.ndarray:
        """
        Performs Centered Log-Ratio (CLR) transformation on the dataset.

        :return np.ndarray: CLR-transformed dataset.
        """

        # Apply log transformation after adding 1 to avoid log(0)
        log_data = np.array(np.log(self.data + 1))

        # Compute mean across columns (features)
        mean = np.mean(log_data, axis=0, keepdims=True)

        return log_data - mean
