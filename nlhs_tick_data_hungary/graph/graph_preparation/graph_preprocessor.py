"""
Nem, időszak kiválasztása
"""
import pandas as pd


class GraphPreprocessor:
    def __init__(self, df: pd.DataFrame, to_type: str, year: str, month: str):
        self.df = df
        self.to_type = to_type
        self.year = year
        self.month = month

        self.select_year_and_month()
        self.select_type()
    # TODO: ez a függvény kerüljön az assistingmethodsba és legyen még egy osztály,
    #  ami a crosstable-t is csinálja, ennek a függvénynek a meghívásával

    # TODO: ennek az osztálynak az lenne a célja, hogy előkészítse a pd.dataframe-t a gráfnak,
    #  vagyis nem kell pl. sparcc esetén nőstény-hím különbség ide, max munkafüzetbe (de akkor már a másiknál is a munkafüzetben legyen megoldva)
    @staticmethod
    def select_type(df, to_type):
        if self.to_type == 'Hím':
            self.df = self.df.filter(like='Male')
        elif self.to_type == 'Nőstény':
            self.df = self.df.filter(like='Female')
        elif self.to_type == '':
            pass

        # Convert the DataFrame values to numeric integer where possible
        self.df = self.df.apply(pd.to_numeric, errors='coerce', downcast='integer')

    def select_year_and_month(self):
        # TODO: ezt a dataloader-be
        self.df.columns = pd.MultiIndex.from_tuples(
            [(year, month, individual) for year, month, individual in self.df.columns],
            names=('Year', 'Month', 'Gender')
        )
        # TODO: kivenni a számokat a dataloader-nél, pl.: 'Female 19' -> 'Female'
        if self.year == '' and self.month == '':
            pass

        if self.year == '' and self.month != '':
            avalaible_combs = [y for y in ['2022', '2023'] if (y, self.month) in self.df.columns]
            self.df = pd.concat([self.df[(y, self.month)] for y in avalaible_combs], axis=1)


        elif self.year != '' and self.month == '':

            self.df = pd.concat(
                [self.df[(self.year, m)] for m in ['January', 'October', 'November', 'December'] if
                 (self.year, m) in self.df.columns], axis=1
            )

        else:
            self.processed_df = self.df[(self.year, self.month)]
