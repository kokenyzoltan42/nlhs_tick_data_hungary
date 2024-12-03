import pandas as pd


class WinterTickPreprocessor:
    """
    Class for preparing the winter tick data for further analysis.

    Attribute(s):
    data: raw winter tick data passed by LoadWinterTickData class
    """
# TODO: Update docstrings
    def __init__(self, data: pd.DataFrame, selected_group: str = None):
        self.data = data

        self.selected_group = selected_group

        self.fixing_columns()

    def fixing_columns(self) -> None:
        """
        Method for fixing the columns of the winter tick data for easier manageability.
        """
        # TODO: Ezeket json-ből kellene beolvasni
        group_1 = ['Neoehrlichia mikurensis',
                   'B.burgdorferi s.s.',
                   'B.afzelii',
                   'Babesia microti',
                   'Rickettsia Catch-all (23-5s rRNA)',
                   'Anaplasma phagocytophilum 1',
                   'Rickettsia helvetica (16s rRNA)',
                   'Rickettsia massiliae (16s rRNA)',
                   'Rickettsia sp. (DnS14)/ raoultii (16s rRNA)'
                   ]

        group_2 = ['Lyme Borrelia catch-all (Rijpkema)',
                   'Lyme Borrelia catch-all (Anna)',
                   'Spotted Fever Group catch-all (23-5s rRNA)',
                   'Rickettsia catch-all (16s rRNA)',
                   'Theileria/Babesia catch-all',
                   'Babesia catch-all 1',
                   'Babesia catch-all 2',
                   'Theileria catch-all',
                   'Ehrlichia/Anaplasma catch-all']

        group_3 = ['Lyme Borrelia catch-all (Rijpkema)',
                   'Lyme Borrelia catch-all (Anna)',
                   'Spotted Fever Group catch-all (23-5s rRNA)',
                   'Rickettsia catch-all (16s rRNA)',
                   'Babesia catch-all 1',
                   'Babesia catch-all 2',
                   'Theileria catch-all',
                   'Ehrlichia/Anaplasma catch-all',
                   'Rickettsia Catch-all (23-5s rRNA)',
                   'Anaplasma phagocytophilum 1']

        # self.data's structure in the beginning is the following:
        # Indices: Name of the Bacteria
        # Columns: Year, Month, Gender-Number
        self.data['Bacteria'] = self.data['18×173']
        self.data = self.data.drop(columns=['18×173'])
        self.data = self.data.set_index('Bacteria')

        if self.selected_group == 'Remove catch-all':
            # There is an instance where 'catch-all' is written with a capital C
            self.data = self.data[~self.data.index.astype(str).str.contains('atch-all')]
        # TODO: dictionary-be helyezni és onnan meghívni, így csúnya
        # TODO: a csoport kiválasztása kerüljön külön függvénybe
        if self.selected_group == '1. csoport':
            self.data = self.data.loc[self.data.index.isin(group_1)]
        if self.selected_group == '2. csoport':
            self.data = self.data.loc[self.data.index.isin(group_2)]
        if self.selected_group == '3. csoport':
            self.data = self.data.loc[self.data.index.isin(group_3)]

        # Renaming the columns for easier manageability
        colos = list(self.data.T.columns)
        colos[0] = 'Year'
        colos[1] = 'Month'
        colos[2] = 'Gender'
        new_df = self.data.T

        new_df.columns = colos

        new_df.set_index(keys=['Year', 'Month', 'Gender'], inplace=True)
        self.data = new_df.T
