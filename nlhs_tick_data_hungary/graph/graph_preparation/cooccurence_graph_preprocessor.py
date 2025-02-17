"""
Itt lesz a különbségek kezelése is, meg a crosstable létrehozása (assistingmethods példányosítása) pl.
"""
import numpy as np

from nlhs_tick_data_hungary.utils.assisting_methods import AssistingMethods


class CooccurenceGraphPreprocessor:
    def __init__(self, df, type_of_data, percentage, year, month):
        self.df = df
        self.type_of_data = type_of_data
        self.percentage = percentage
        self.year = year
        self.month = month

        self.num_of_samples = None
        self.epsilon = 1e-5  # Small value to prevent division by zero

        self.preprocessed_df = None

    def create_crosstable_based_on_type_of_data(self):
        pass

    def convert_to_percentage(self):
        pass
