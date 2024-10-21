import pandas as pd


class InermisPreprocessor:
    def __init__(self, data: pd.DataFrame):
        self.data = data

        self.fixing_columns()

    def fixing_columns(self):
        self.data['Bacteria'] = self.data['18×173']
        self.data = self.data.drop(columns=['18×173'])
        self.data = self.data.set_index('Bacteria')

        # TODO: ezt a részt szépíteni
        colos = list(self.data.T.columns)
        colos[0] = 'Year'
        colos[1] = 'Month'
        colos[2] = 'Gender'
        new_df = self.data.T

        new_df.columns = colos

        new_df.set_index(keys=['Year', 'Month', 'Gender'], inplace=True)
        self.data = new_df.T
