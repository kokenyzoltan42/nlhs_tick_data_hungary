import numpy as np
import pandas as pd

from nlhs_tick_data_hungary.utils.assisting_methods import AssistingMethods
from nlhs_tick_data_hungary.graph.graph_preparation.general_graph_preprocessor import GeneralGraphPreprocessor


class CooccurenceGraphPreprocessor:
    """
    A class to preprocess co-occurrence graphs from a given DataFrame.

    df (DataFrame): The input data as a DataFrame.
    type_of_data (str): The type of data to process (e.g., 'Nőstények', 'Hímek', etc.).
    convert_to_percentage (bool): Whether to convert results to percentage.
    year (str): The year for which the data is being processed (e.g., '2023')
    month (str): The month for which the data is being processed (e.g., 'January')
    num_of_samples (int): The number of samples in the preprocessed DataFrame.
    epsilon (float): A small value to prevent division by zero in calculations.
    general_preprocessed_df (DataFrame): The DataFrame after general preprocessing.
    preprocessed_df (DataFrame): The final preprocessed DataFrame based on the type of data.
    """

    def __init__(self, df: pd.DataFrame, type_of_data: str, convert_to_percentage: bool, year: str, month: str):
        """
        Initializes the CooccurenceGraphPreprocessor with provided data and parameters.

        :param pd.DataFrame df: The input DataFrame containing the raw data.
        :param str type_of_data: The type of data to process (e.g., 'Nőstények', 'Hímek', etc.).
        :param bool convert_to_percentage: Indicates if the output should be in percentage.
        :param str year: The year for which the data is being processed (e.g., '2023')
        :param str month: The month for which the data is being processed (e.g., 'January')
        """
        self.df = df
        self.type_of_data = type_of_data
        self.convert_to_percentage = convert_to_percentage
        self.year = year
        self.month = month

        self.num_of_samples = None
        self.epsilon = 1e-5  # Small value to prevent division by zero

        self.general_preprocessed_df = None
        self.preprocessed_df = None

    def run(self):
        """
        Runs the preprocessing steps: filtering, transforming, creating crosstable, and applying percentage.
        """
        self.filter_and_transform_dataframe()
        self.create_crosstable_based_on_type_of_data()
        self.apply_percentage()

    def filter_and_transform_dataframe(self):
        """
        Filters and transforms the input DataFrame based on the specified type of data.
        This method utilizes GeneralGraphPreprocessor to prepare the DataFrame for further processing.
        """
        preprocessor = GeneralGraphPreprocessor(df=self.df,
                                                to_type=self.type_of_data,
                                                year=self.year,
                                                month=self.month)
        # This DataFrame has been reduced to a specific timeframe and, if the `type_of_data` attribute is
        # either 'Nőstények', 'Hímek', or 'Összes', then this DataFrame only contains data for
        # either females, males, or all genders. If `type_of_data` is something else then this preprocessing only
        # changes the timeframe.
        self.general_preprocessed_df = preprocessor.preprocessed_df

        # Store the number of samples in the DataFrame (for the calculation of percentages and possibly for plotting)
        self.num_of_samples = self.general_preprocessed_df.shape[1]

        # If the type is either 'Nőstények', 'Hímek', or 'Összes', then the previous preprocessing already selected
        # the type so no further transformation needed
        if self.type_of_data in ['Nőstények', 'Hímek', 'Összes']:
            self.preprocessed_df = AssistingMethods.create_crosstable(df=self.general_preprocessed_df)

    def create_crosstable_based_on_type_of_data(self):
        """
        Creates crosstables for male and female data based on the preprocessed data to calculate the differences between
        male and female data if applicable.
        """
        if self.type_of_data in ['Különbség', 'Nőstény - Hím', 'Hím - Nőstény']:
            # Load data for both genders to calculate differences
            fem_df = AssistingMethods.select_type(df=self.general_preprocessed_df,
                                                  to_type='Nőstények')
            male_df = AssistingMethods.select_type(df=self.general_preprocessed_df,
                                                   to_type='Hímek')

            # Create crosstables for female and male data and fill missing values with zero
            fem_crosstable, male_crosstable = map(
                lambda df: AssistingMethods.create_crosstable(df).fillna(0), [fem_df, male_df]
            )

            # Define operations for calculating differences (to avoid so many 'if' operations)
            diff_calc_operations = {
                'Nőstény - Hím': fem_crosstable - male_crosstable,
                'Hím - Nőstény': male_crosstable - fem_crosstable,
                'Különbség': abs(fem_crosstable - male_crosstable)
            }

            # Define operations for calculating differences in percentage (to avoid so many 'if' operations)
            diff_calc_operations_percentage = {
                'Hím - Nőstény': lambda: np.log((male_crosstable + self.epsilon) / (fem_crosstable + self.epsilon)),
                'Nőstény - Hím': lambda: np.log((fem_crosstable + self.epsilon) / (male_crosstable + self.epsilon)),
                'Különbség': lambda: abs(np.log((male_crosstable + self.epsilon) / (fem_crosstable + self.epsilon)))
            }

            # Select the appropriate calculation based on whether to convert to percentage
            if self.convert_to_percentage:
                self.preprocessed_df = diff_calc_operations_percentage.get(self.type_of_data, lambda: None)()
            else:
                self.preprocessed_df = diff_calc_operations.get(self.type_of_data, None)

    def apply_percentage(self):
        """
        Applies percentage conversion to the preprocessed DataFrame if required.
        Only applies to types that are not 'Különbség', 'Nőstény - Hím', or 'Hím - Nőstény'.
        """
        if self.convert_to_percentage and self.type_of_data not in ['Különbség', 'Nőstény - Hím', 'Hím - Nőstény']:
            self.preprocessed_df = (self.preprocessed_df.fillna(0) / self.num_of_samples * 100).round(0)
