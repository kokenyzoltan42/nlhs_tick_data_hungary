"""
Itt lesz a különbségek kezelése is, meg a crosstable létrehozása (assistingmethods példányosítása) pl.
"""
import numpy as np

from nlhs_tick_data_hungary.utils.assisting_methods import AssistingMethods
from nlhs_tick_data_hungary.graph.graph_preparation.general_graph_preprocessor import GeneralGraphPreprocessor


class CooccurenceGraphPreprocessor:
    def __init__(self, df, type_of_data, convert_to_percentage, year, month):
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
        self.filter_and_transform_dataframe()
        self.create_crosstable_based_on_type_of_data()
        self.apply_percentage()

    def filter_and_transform_dataframe(self):
        preprocessor = GeneralGraphPreprocessor(df=self.df,
                                                to_type=self.type_of_data,
                                                year=self.year,
                                                month=self.month)
        # This is DataFrame has been reduced to a specific timeframe(?) and if the
        # `type_of_data` attribute is either 'Nőstények', 'Hímek' or 'Összes', then this
        # DataFrame only contains either data of females, males or every gender
        self.general_preprocessed_df = preprocessor.preprocessed_df

        self.num_of_samples = self.general_preprocessed_df.shape[1]

        if self.type_of_data in ['Nőstények', 'Hímek', 'Összes']:
            self.preprocessed_df = AssistingMethods.create_crosstable(df=self.general_preprocessed_df)

    def create_crosstable_based_on_type_of_data(self):
        if self.type_of_data in ['Különbség', 'Nőstény - Hím', 'Hím - Nőstény']:
            # Load data for both genders to calculate differences
            fem_df = AssistingMethods.select_type(df=self.general_preprocessed_df,
                                                  to_type='Nőstények')
            male_df = AssistingMethods.select_type(df=self.general_preprocessed_df,
                                                   to_type='Hímek')

            fem_crosstable, male_crosstable = map(
                lambda df: AssistingMethods.create_crosstable(df).fillna(0), [fem_df, male_df]
            )

            diff_calc_operations = {
                'Nőstény - Hím': fem_crosstable - male_crosstable,
                'Hím - Nőstény': male_crosstable - fem_crosstable,
                'Különbség': abs(fem_crosstable - male_crosstable)
            }

            diff_calc_operations_percentage = {
                'Hím - Nőstény': lambda: np.log((male_crosstable + self.epsilon) / (fem_crosstable + self.epsilon)),
                'Nőstény - Hím': lambda: np.log((fem_crosstable + self.epsilon) / (male_crosstable + self.epsilon)),
                'Különbség': lambda: abs(np.log((male_crosstable + self.epsilon) / (fem_crosstable + self.epsilon)))
            }

            if self.convert_to_percentage:
                self.preprocessed_df = diff_calc_operations_percentage.get(self.type_of_data, lambda: None)()
            else:
                self.preprocessed_df = diff_calc_operations.get(self.type_of_data, None)

            # Régi megoldás
            # if self.convert_to_percentage:
            #    if self.type_of_data == 'Hím - Nőstény':
            #        self.preprocessed_df = np.log((male_crosstable + self.epsilon) / (fem_crosstable + self.epsilon))
            #    if self.type_of_data == 'Nőstény - Hím':
            #        self.preprocessed_df = np.log((fem_crosstable + self.epsilon) / (male_crosstable + self.epsilon))
            #    if self.type_of_data == 'Különbség':
            #        self.preprocessed_df = abs(np.log((male_crosstable + self.epsilon) /
            #                                          (fem_crosstable + self.epsilon)))
            #
            # else:
            #
            #    if self.type_of_data == 'Nőstény - Hím':
            #        self.preprocessed_df = fem_crosstable - male_crosstable
            #    elif self.type_of_data == 'Hím - Nőstény':
            #        self.preprocessed_df = male_crosstable - fem_crosstable
            #    elif self.type_of_data == 'Különbség':
            #        self.preprocessed_df = abs(fem_crosstable - male_crosstable)

    def apply_percentage(self):
        if self.convert_to_percentage and self.type_of_data not in ['Különbség', 'Nőstény - Hím', 'Hím - Nőstény']:
            self.preprocessed_df = (self.preprocessed_df.fillna(0) / self.num_of_samples * 100).round(2)
