import pandas as pd

from nlhs_tick_data_hungary.data_preprocessor.inermis_preprocessor import InermisPreprocessor


class LoadWinterTickData:
    """
    Class for loading and filtering winter tick data (H. inermis).
    This class utilizes the InermisPreprocessor to handle the data preprocessing and provides
    filtering functionality based on gender, year, and month.

    Attributes:
    ----------
    data : The original DataFrame containing winter tick data.
    preprocessor : An instance of the InermisPreprocessor class for preprocessing the data.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the LoadWinterTickData class with the raw data and preprocessor.

        :param data: The DataFrame containing raw winter tick data.
        """
        self.data = data
        self.preprocessor = InermisPreprocessor(data=self.data)

    def run(self, gender: str, year: str, month: str) -> pd.DataFrame:
        """
        Run the process to filter winter tick data based on the specified gender, year, and month.

        :param gender: The gender to filter by ('Male', 'Female', or 'All').
        :param year: The year to filter by (e.g., '2022', '2023'). If an empty string, then there is no year filter.
        :param month: The month to filter by (e.g., 'January', 'October'). If an empty string, then there is
         no month filter.
        :return: Filtered DataFrame containing winter tick data based on the specified filters.
        """
        # Filter the data using the preprocessor's data and the provided parameters.
        winter_tick_data = self.get_tick_data(data=self.preprocessor.data,
                                              gender=gender,
                                              year=year,
                                              month=month)

        return winter_tick_data

    def get_tick_data(self,
                      data: pd.DataFrame,
                      gender: str,
                      year: str,
                      month: str) -> pd.DataFrame:
        """
        Get tick data filtered by gender, year, and month. Supports different combinations of filters:
        - No year and no month: Returns the entire dataset filtered by gender.
        - Only month: Concatenates data across all years for the specified month.
        - Only year: Concatenates data across all months for the specified year.
        - Both year and month: Returns data for the specified year and month.

        :param data: The preprocessed winter tick data.
        :param gender: The gender to filter by ('Male', 'Female', or 'All').
        :param year: The year to filter by (e.g., '2022', '2023'). Leave empty for no year filter.
        :param month: The month to filter by (e.g., 'January', 'October'). Leave empty for no month filter.
        :return: A filtered DataFrame based on the provided filters.
        """
        # No year and no month: Return the entire dataset filtered by gender
        if year == '' and month == '':
            tick_data = self.select_gender(df=data, gender=gender)
            return tick_data.astype(float)

        # Create a MultiIndex for easier handling of the columns based on year, month, and gender
        data.columns = pd.MultiIndex.from_tuples(
            [(year, month, individual) for year, month, individual in data.columns],
            names=['Year', 'Month', 'Gender']
        )

        # Only month is provided: Concatenate data across all available years for the specified month
        if year == '' and month != '':
            available_years = [y for y in ['2022', '2023'] if (y, month) in data.columns]
            concatonated = pd.concat([data[(y, month)] for y in available_years], axis=1)

        # Only year is provided: Concatenate data across all months for the specified year
        elif year != '' and month == '':
            concatonated = pd.concat(
                [data[(year, m)] for m in ['January', 'October', 'November', 'December'] if
                 (year, m) in data.columns], axis=1
            )

        # Both year and month are provided: Return data for the specified year and month
        else:
            concatonated = data[(year, month)]

        # Filter the concatenated data by gender
        tick_data = self.select_gender(df=concatonated, gender=gender)

        return tick_data.astype(float)

    @staticmethod
    def select_gender(df: pd.DataFrame, gender: str) -> pd.DataFrame:
        """
        Filter the tick data based on the specified gender. If 'All' is specified, no filtering is applied.
        If neither 'Male', 'Female', nor 'All' is provided, an error is raised.

        :param df: DataFrame to filter by gender.
        :param gender: The gender to filter by ('Male', 'Female', or 'All').
        :return: Filtered or unfiltered DataFrame based on the provided gender.
        """
        if gender == 'Male' or gender == 'Female':
            # Filter the DataFrame for the specified gender
            df = df.filter(like=gender)

        elif gender == 'All':
            # If 'All' is specified, return the unfiltered DataFrame
            pass

        else:
            # Raise an error if an invalid gender is provided
            raise ValueError("Invalid gender. Gender must be 'Male', 'Female', or 'All'.")

        # Convert the DataFrame values to numeric, coercing errors and downcasting to integer where possible
        df = df.apply(pd.to_numeric, errors='coerce', downcast='integer')
        return df
