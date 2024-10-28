import numpy as np
import pandas as pd
import re


# TODO: több osztályra szedni?

class PilisPreprocessor:
    """
    A data preprocessing class for tick collection data from Pilis region.

    This class handles data cleaning, normalization, and organization of tick
    gathering records, transforming raw input data into a usable format for analysis.

    Attributes:
    data: The raw tick data as a pandas DataFrame.
    remove_reds: A flag to indicate whether to remove specific rows of data (for erroneous entries).
    """

    def __init__(self, data: pd.DataFrame, remove_reds: bool = True):
        """
        Initializes the PilisPreprocessor class with the provided data.

        :param data: Raw tick data as a pandas DataFrame.
        :param remove_reds: A boolean flag to remove specific erroneous entries from the data.
        """
        self.data = data
        self.remove_reds = remove_reds

        # Start the preprocessing pipeline
        self.run()

    def run(self) -> None:
        """
        Runs the sequence of preprocessing steps on the tick data.

        The steps include adjusting column names, splitting temperature and RH columns,
        removing specified erroneous entries, filling missing data, adjusting indices,
        and normalizing tick gathering numbers.
        """
        self.adjust_columns()
        self.split_temps_and_rhs()
        self.remove_reds_from_table()
        self.fill_missing_data()
        self.adjust_indices()
        self.normalize_tick_gathering()

    @staticmethod
    def split_min_max(temp: pd.Series) -> pd.Series:
        """
        Splits a series containing temperature or RH values into minimum and maximum values.

        If a value is a single number, both min and max will be set to that number. If it's an interval
        (e.g., "10-20"), it splits it into min and max.

        :param temp: A pandas Series containing temperature or RH values to be split.
        :return: A pandas Series containing minimum and maximum values.
        """
        temp = str(temp).replace(',', '.').strip()
        if re.match(pattern=r"^\s*\d+([.,]\d+)?\s*$", string=temp):
            # If there is only one number
            min_val = max_val = float(temp)
            return pd.Series([min_val, max_val])
        elif re.match(pattern=r"^\s*\d+([.,]\d+)?\s*-\s*\d+([.,]\d+)?\s*$", string=temp):
            # If there is an interval
            min_val, max_val = map(float, temp.split('-'))
            return pd.Series([min_val, max_val])
        else:
            return pd.Series([None, None])  # Return None if the format is invalid

    @staticmethod
    def adjust_months(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adjusts the 'Date' column in the DataFrame to ensure continuity in month values.

        This function checks consecutive rows for the same month and decrements the previous
        month if a duplication is found.

        :param df: The DataFrame containing a 'Date' column.
        :return: The DataFrame with adjusted month values.
        """
        prev_month = None
        for idx, row in df.iterrows():
            if prev_month == row['Date']:
                df.at[idx + 1, 'Date'] += 1
            prev_month = row['Date']
        return df

    def adjust_columns(self) -> None:
        """
        Renames and adjusts the columns of the DataFrame for consistency and clarity.

        This function also drops the first row (often a header row) and resets the index.
        It converts specific columns to float data types to ensure numerical operations can be performed.
        """
        # Rename columns for clarity
        self.data = self.data.rename(columns={
            "Unnamed: 7": "RH(%)",
            "Kullancs mennyiség/faj (db)": "I. ricinus nőstény",
            "Unnamed: 11": "I. ricinus hím",
            "Unnamed: 12": "I. ricinus nimfa",
            "Unnamed: 13": "I. lárva",
            "Unnamed: 14": "H. inermis nőstény",
            "Unnamed: 15": "H. inermis hím",
            "Unnamed: 16": "H. inermis nimfa",
            "Unnamed: 17": "H. concinna nőstény",
            "Unnamed: 18": "H. concinna hím",
            "Unnamed: 19": "H. concinna nimfa",
            "Unnamed: 20": "H. lárva",
            "Unnamed: 21": "D. marginatus nőstény",
            "Unnamed: 22": "D. marginatus hím",
            "Unnamed: 23": "D. marginatus nimfa",
            "Unnamed: 24": "D. marginatus lárva",
            "Unnamed: 25": "D. reticulatus nőstény",
            "Unnamed: 26": "D. reticulatus hím",
            "Unnamed: 27": "D. reticulatus nimfa",
            "Unnamed: 28": "D. reticulatus lárva",
        })

        # Drop the first row and reset the index
        self.data = self.data.drop(index=0).reset_index().drop(columns="index")

        # Defining columns that need to be converted to float
        columns_to_float = [
            'I. ricinus hím', 'I. ricinus nőstény', 'I. ricinus nimfa', 'I. lárva',
            'H. inermis nőstény', 'H. inermis hím', 'H. inermis nimfa',
            'H. concinna nőstény', 'H. concinna hím', 'H. concinna nimfa', 'H. lárva',
            'D. marginatus nőstény', 'D. marginatus hím', 'D. marginatus nimfa', 'D. marginatus lárva',
            'D. reticulatus nőstény', 'D. reticulatus hím', 'D. reticulatus nimfa', 'D. reticulatus lárva',
            'Gyűjtők száma', 'Összes kullancs (db)'
        ]

        # Convert specific columns to float
        self.data[columns_to_float] = self.data[columns_to_float].astype(float)
        self.data["Gyűjtés időtartama (h)"] = self.data["Gyűjtés időtartama (h)"].str.replace(',', '.').astype(float)

    def split_temps_and_rhs(self) -> None:
        """
        Splits the 'T (°C)' and 'RH(%)' columns into separate minimum and maximum columns.

        This function calls the split_min_max method to process each respective column
        and then drops the original columns after extraction.
        """
        self.data[['Min - T (°C)', 'Max - T (°C)']] = self.data['T (°C)'].apply(self.split_min_max)
        self.data[['Min - RH(%)', 'Max - RH(%)']] = self.data['RH(%)'].apply(self.split_min_max)

        # Drop the original columns
        self.data.drop(columns=['T (°C)', 'RH(%)'], inplace=True)

    def remove_reds_from_table(self) -> None:
        """
        Removes specific erroneous rows from the DataFrame based on predefined dates.

        If the remove_reds attribute is set to True, this function filters out rows
        with collection dates that are known to be erroneous.
        """
        if self.remove_reds:
            datumok = ['2015-05-13', '2015-06-05', '2015-07-01', '2016-06-22']
            self.data = self.data[~self.data['Gyűjtési dátum'].isin(datumok)]

            # Reset the index after filtering
            self.data.reset_index(drop=True, inplace=True)

    def fill_missing_data(self) -> None:
        """
        Fills missing values in the DataFrame with appropriate defaults or previous values.

        This function ensures that the 'Gyűjtők száma' column is filled with data from
        the 'Eredeti csövek száma' column where applicable.
        """
        self.data = self.data.fillna(np.nan)  # Fill with NaN for clarity
        self.data['Gyűjtők száma'] = self.data['Gyűjtők száma'].fillna(self.data['Eredeti csövek száma'])

    def adjust_indices(self) -> None:
        """
        Adjusts the DataFrame indices based on the collection dates.

        This method converts the 'Gyűjtési dátum' to a period format (monthly),
        groups the data by date, and aggregates the columns accordingly.
        Additionally, it reindexes the DataFrame to cover the full date range.
        """
        # Convert collection dates to periods
        self.data['Date'] = pd.to_datetime(self.data['Gyűjtési dátum']).dt.to_period('M')

        # Adjust month values for continuity
        self.data = self.adjust_months(self.data)

        # Group by date using resample for monthly aggregation and calculate mean for numeric columns
        self.data = self.data.resample('M', on='Date').agg({
            'Min - T (°C)': 'mean',
            'Max - T (°C)': 'mean',
            'Min - RH(%)': 'mean',
            'Max - RH(%)': 'mean',
            'Gyűjtés helye': 'first',  # Keep the first non-numeric column as it is
            **{col: 'sum' for col in self.data.columns if col not in ['Date',
                                                                      'Min - T (°C)', 'Max - T (°C)',
                                                                      'Min - RH(%)', 'Max - RH(%)',
                                                                      'Gyűjtés helye']}
        }).reset_index()

        # Set 'Date' as index and drop unnecessary columns
        self.data.set_index('Date', inplace=True)
        self.data = self.data.drop(columns='Gyűjtési dátum', errors='ignore')

        # Reindex to include a full range of dates
        full_index = pd.date_range(start='2011-04', end='2024-08', freq='M').to_period('M')
        self.data = self.data.reindex(full_index, fill_value=np.nan)

    def normalize_tick_gathering(self) -> None:
        """
        Normalizes the number of ticks gathered by the number of collectors.

        This function creates a new column that represents the normalized number of ticks
        collected per collector, allowing for better comparative analysis.
        """
        self.data['Normált gyűjtött kullancsok'] = self.data['Összes kullancs (db)'] / self.data['Gyűjtők száma']
