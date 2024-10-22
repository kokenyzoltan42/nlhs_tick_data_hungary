import pandas as pd


class WinterTickPreprocessor:
    """
    Class for preparing the winter tick data for further analysis.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the preprocessor with the provided DataFrame.

        :param data: DataFrame containing winter tick data.
        """
        self.data = data
        self.preprocess_data()

    def preprocess_data(self) -> None:
        """
        Main method to preprocess the data by fixing columns and setting the index.
        """
        self.rename_and_set_index()
        self.restructure_data()

    def rename_and_set_index(self) -> None:
        """
        Rename the '18×173' column to 'Bacteria' and set it as the index.
        """
        self.data.rename(columns={'18×173': 'Bacteria'}, inplace=True)
        self.data.set_index('Bacteria', inplace=True)

    def restructure_data(self) -> None:
        """
        Restructure the DataFrame by transposing it and setting meaningful multi-index.
        """
        # Get current columns and assign meaningful names
        new_columns = ['Year', 'Month', 'Gender'] + list(self.data.index[3:])

        # Transpose the DataFrame and set new column names
        self.data = self.data.T
        self.data.columns = new_columns

        # Set a multi-index with Year, Month, and Gender
        self.data.set_index(keys=['Year', 'Month', 'Gender'], inplace=True)

    def get_preprocessed_data(self) -> pd.DataFrame:
        """
        Get the preprocessed DataFrame.

        :return: Preprocessed DataFrame.
        """
        return self.data.T  # Transpose back to original orientation if necessary
