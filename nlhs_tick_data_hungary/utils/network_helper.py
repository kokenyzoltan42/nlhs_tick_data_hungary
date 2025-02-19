import numpy as np
import pandas as pd


class NetworkHelper:
    """
    A utility class that provides helper methods for data processing, such as creating a crosstable and filtering
    DataFrame columns based on a specified type.
    """

    @staticmethod
    def create_crosstable(df: pd.DataFrame) -> pd.DataFrame:
        """
        Method for generating a crosstable for the cooccurence network. The number in the ith row nad jth column means
        how many times the ith AND the jth bactria was found on every tick. The diagonal values are replaced with NaN.

        :param pd.DataFrame df: A DataFrame where rows are the bacteria and columns are the samples

        :return pd.DataFrame: Crosstable DataFrame with NaN on the diagonal
        """
        # Compute the dot product of the DataFrame with its transpose
        final = df.dot(df.T).astype(float)

        # Replace diagonal elements with NaN
        np.fill_diagonal(final.values, np.nan)

        return final

    @staticmethod
    def select_type(df: pd.DataFrame, to_type: str) -> pd.DataFrame:
        """
        Filters the DataFrame columns based on the specified type.
        It retains columns that contain 'Male' or 'Female' in their names,
        or returns the unmodified DataFrame if 'Összes' (All) is selected.


        :param pd.DataFrame df: A DataFrame with column names indicating gender categories
        :param str to_type: The type of selection - 'Hímek' (Males), 'Nőstények' (Females), or 'Összes' (All)

        :return pd.DataFrame: Filtered DataFrame based on the selected type
        """
        if to_type == 'Hímek':
            # Keep only columns that contain 'Male'
            df = df.filter(like='Male')
        elif to_type == 'Nőstények':
            # Keep only columns that contain 'Female'
            df = df.filter(like='Female')
        elif to_type == 'Összes':
            # No filtering necessary
            pass

        return df
