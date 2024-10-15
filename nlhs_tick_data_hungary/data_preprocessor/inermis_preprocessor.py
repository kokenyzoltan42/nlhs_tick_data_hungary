import pandas as pd


class InermisPreprocessor:
    def __init__(self, data):
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

        new_df.set_index(['Year', 'Month', 'Gender'], inplace=True)
        self.data = new_df.T

    @staticmethod
    def select_gender(df, gender: str):
        # TODO: szépíteni, így nem látszik, hogy ha gender='All', akkor nem filterezik
        if gender == 'Male':
            df = df.filter(like='Female')
        elif gender == 'Female':
            df = df.filter(like='Male')

        df = df.apply(pd.to_numeric, errors='coerce', downcast='integer')
        return df

    def get_winter_tick_data(self, gender: str, year: str, month: str):
        # Se év, se hónap -> teljes adattábla
        if year == '' and month == '':
            tick_data = self.select_gender(df=self.data, gender=gender)
            return tick_data.astype(float)

        # Multiindexeés a könnyebb kezelhetőségért
        self.data.columns = pd.MultiIndex.from_tuples(
            [(year, month, individual) for year, month, individual in self.data.columns],
            names=['Year', 'Month', 'Gender']
        )

        # Csak hónap van megadva -> az összes év (amiben benne van ez a hónap) összevonjuk(?)
        if year == '' and month != '':
            available_years = [y for y in ['2022', '2023'] if (y, month) in self.data.columns]
            concatonated = pd.concat([self.data[(y, month)] for y in available_years], axis=1)

        # Csak év van megadva -> azon évbeli összes hónap
        elif year != '' and month == '':
            concatonated = pd.concat([self.data[(year, m)] for m in ['January', 'October', 'November', 'December'] if
                                      (year, m) in self.data.columns], axis=1)

        # Meg van adva az év és a hónap is
        else:
            concatonated = self.data[(year, month)]

        # Filter by gender and return the result
        tick_data = self.select_gender(df=concatonated, gender=gender)
        return tick_data.astype(float)
