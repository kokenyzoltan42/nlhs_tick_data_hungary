import pandas as pd

from nlhs_tick_data_hungary.utils.assisting_methods import AssistingMethods


class GeneralNetworkPreprocessor:
    """
    Prepares a pandas DataFrame for network processing by selecting relevant data and structuring it by time.

    - preprocessed_df (pd.DataFrame): The preprocessed DataFrame (with selected type and time)
    """

    def __init__(self, df: pd.DataFrame, to_type: str, year: str, month: str):
        """
        Initializes the preprocessor with a DataFrame and filtering parameters.

        :param pd.DataFrame df: The input DataFrame containing raw data
        :param str to_type: The type of data to select
        :param str year: The year filter, or an empty string to select all years
        :param str year: The month filter, or an empty string to select all months
        """
        self.df = df
        self.to_type = to_type
        self.year = year
        self.month = month

        self.preprocessed_df = None

        # Select data based on type (gender category)
        self.select_type_of_data()

        # Prepare DataFrame by structuring it with time-based indexing
        self.prepare_dataframe_by_time()

    def select_type_of_data(self):
        """
        Filters the DataFrame based on the specified type (e.g., 'Male', 'Female').
        Converts values to numeric format where applicable.
        """
        self.df = AssistingMethods.select_type(df=self.df, to_type=self.to_type)

        # Convert the DataFrame values to numeric integers where possible
        self.df = self.df.apply(pd.to_numeric, errors='coerce', downcast='integer')

    def prepare_dataframe_by_time(self) -> None:
        """
        Method for filtering data based on specified year and month values.
        """

        if self.year == '' and self.month == '':
            self.preprocessed_df = self.df
            return

        # Filter based on available year-month combinations if only the month is specified
        if self.year == '' and self.month != '':
            available_combs = [y for y in ['2022', '2023'] if (y, self.month) in self.df.columns]
            self.preprocessed_df = pd.concat([self.df[(y, self.month)] for y in available_combs], axis=1)

        # Filter based on available months if only the year is specified
        elif self.year != '' and self.month == '':
            self.preprocessed_df = pd.concat(
                [self.df[(self.year, m)] for m in ['January', 'October', 'November', 'December'] if
                 (self.year, m) in self.df.columns], axis=1
            )
        else:
            # Select data for the specified year and month
            self.preprocessed_df = self.df[(self.year, self.month)]
