import pandas as pd

from nlhs_tick_data_hungary.data_preprocessor.inermis_preprocessor import InermisPreprocessor


class LoadWinterTickData:
    """
    Class for loading data of the winter tick
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data

        self.preprocessor = InermisPreprocessor(data=self.data)

    def run(self, gender: str, year: str, month: str) -> pd.DataFrame:
        """

        :return:
        """
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

        :param data:
        :param gender:
        :param year:
        :param month:
        :return:
        """
        # Se év, se hónap -> teljes adattábla
        if year == '' and month == '':
            tick_data = self.select_gender(df=data, gender=gender)
            return tick_data.astype(float)

        # Multiindexelés a könnyebb kezelhetőségért
        data.columns = pd.MultiIndex.from_tuples(
            [(year, month, individual) for year, month, individual in data.columns],
            names=['Year', 'Month', 'Gender']
        )

        # Csak hónap van megadva -> az összes év (amiben benne van ez a hónap) összevonjuk(?)
        if year == '' and month != '':
            available_years = [y for y in ['2022', '2023'] if (y, month) in data.columns]
            concatonated = pd.concat([data[(y, month)] for y in available_years], axis=1)

        # Csak év van megadva -> azon évbeli összes hónap
        elif year != '' and month == '':
            concatonated = pd.concat(
                [data[(year, m)] for m in ['January', 'October', 'November', 'December'] if
                 (year, m) in data.columns], axis=1
            )

        # Meg van adva az év és a hónap is
        else:
            concatonated = data[(year, month)]

        # Filter by gender and return the result
        tick_data = self.select_gender(df=concatonated,
                                       gender=gender)

        return tick_data.astype(float)

    @staticmethod
    def select_gender(df: pd.DataFrame, gender: str):
        """
        Select rows based on gender. If 'All' is provided, no filtering is applied.
        If neither 'Male', 'Female', nor 'All' is provided, an error is raised.

        :param df: DataFrame to filter
        :param gender: 'Male', 'Female', or 'All'
        :return: Filtered or unfiltered DataFrame
        """

        if gender == 'Male' or gender == 'Female':
            df = df.filter(like=gender)

        elif gender == 'All':
            # Ha 'All', akkor nem történik filterelés, az eredeti DataFrame-et adja vissza
            pass

        else:
            # Ha nem érvényes érték van megadva, hibát dobunk
            raise ValueError("Invalid gender. Gender must be 'Male', 'Female', or 'All'.")

        df = df.apply(pd.to_numeric, errors='coerce', downcast='integer')
        return df
