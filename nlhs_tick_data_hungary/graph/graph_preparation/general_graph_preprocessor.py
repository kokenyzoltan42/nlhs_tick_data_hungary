"""
Nem, időszak kiválasztása
"""
import pandas as pd

from nlhs_tick_data_hungary.utils.assisting_methods import AssistingMethods


class GeneralGraphPreprocessor:
    def __init__(self, df: pd.DataFrame, to_type: str, year: str, month: str):
        self.df = df
        self.to_type = to_type
        self.year = year
        self.month = month

        self.preprocessed_df = None

        self.prepare_dataframe_by_time()
        self.select_type_of_data()

    # TODO: ennek az osztálynak az lenne a célja, hogy előkészítse a pd.dataframe-t a gráfnak
    def select_type_of_data(self):
        self.df = AssistingMethods.select_type(df=self.df,
                                               to_type=self.to_type)

        # Convert the DataFrame values to numeric integer where possible
        self.df = self.df.apply(pd.to_numeric, errors='coerce', downcast='integer')

    def prepare_dataframe_by_time(self) -> None:
        # TODO: ezt a dataloader-be (és kivenni a számokat a dataloader-nél, pl.: 'Female 19' -> 'Female')
        self.df.columns = pd.MultiIndex.from_tuples(
            [(year, month, individual) for year, month, individual in self.df.columns],
            names=('Year', 'Month', 'Gender')
        )
        if self.year == '' and self.month == '':
            return

        mask = (self.df.columns.get_level_values('Year') == self.year) if self.year else True
        mask &= (self.df.columns.get_level_values('Month') == self.month) if self.month else True

        self.preprocessed_df = self.df.loc[:, mask]

        # TODO: erre valszeg van valami elegánsabb megoldás
        # if self.year == '' and self.month != '':
        #    avalaible_combs = [y for y in ['2022', '2023'] if (y, self.month) in self.df.columns]
        #    self.preprocessed_df = pd.concat([self.df[(y, self.month)] for y in avalaible_combs], axis=1)
        #
        # elif self.year != '' and self.month == '':
        #    self.preprocessed_df = pd.concat(
        #        [self.df[(self.year, m)] for m in ['January', 'October', 'November', 'December'] if
        #         (self.year, m) in self.df.columns], axis=1
        #    )
        #else:
        #    self.preprocessed_df = self.df[(self.year, self.month)]
