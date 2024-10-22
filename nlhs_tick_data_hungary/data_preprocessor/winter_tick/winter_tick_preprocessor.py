import pandas as pd


class WinterTickPreprocessor:
    """
    Class for preparing the winter tick data for further analysis.

    Attribute(s):
    data: raw winter tick data passed by LoadWinterTickData class
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data

        self.fixing_columns()

    def fixing_columns(self) -> None:
        """
        Method for fixing the columns of the winter tick data for easier manageability.
        """

        # self.data's structure in the beginning is the following:
        # Indices: Name of the Bacteria
        # Columns: Year, Month, Gender-Number
        self.data['Bacteria'] = self.data['18×173']
        self.data = self.data.drop(columns=['18×173'])
        self.data = self.data.set_index('Bacteria')

        # Renaming the columns for easier manageability
        colos = list(self.data.T.columns)
        colos[0] = 'Year'
        colos[1] = 'Month'
        colos[2] = 'Gender'
        new_df = self.data.T

        new_df.columns = colos

        new_df.set_index(keys=['Year', 'Month', 'Gender'], inplace=True)
        self.data = new_df.T
