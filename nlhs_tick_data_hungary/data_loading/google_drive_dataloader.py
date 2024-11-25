import json
from typing import Tuple

import numpy as np
import pandas as pd
import re

from nlhs_tick_data_hungary import url_path
from nlhs_tick_data_hungary.data_loading.GoogleDataDownLoader import GoogleDataDownloader


class GoogleDriveDataloader:
    """
    A class to load data from Google Drive, specifically Lyme disease statistics and tick data.

    This class handles the following:
    - Loading the number of Lyme disease cases by year and month.
    - Loading tick data from Pilisszentkereszt.
    - Loading data on winter ticks (H. inermis).

    Attributes:
    ----------
    gsheet_url_pilis : str
        URL of the Google Sheet containing Pilis tick data.
    gsheet_url_inermis : str
        URL of the Google Sheet containing Inermis tick data.
    pilis_data : DataFrame containing the tick data from Pilisszentkereszt.
    inermis_data : DataFrame containing the tick data from H. inermis.
    lyme_m : pd.Series
        Monthly Lyme disease cases.
    lyme_y : pd.Series
        Yearly Lyme disease cases.
    """
# TODO: docstring-ek kiegészítése a csapadékos adatokkal
    def __init__(self):
        """
        Initializes the GoogleDriveDataloader with URLs and loads the data from the given Google Sheets.
        """

        # Load data from Google Sheets as CSV
        with open(url_path + f'/links.json', 'r+') as file:
            result = json.load(file)
        # self.pilis_data = pd.read_csv(self.convert_google_sheet_url(gsheet_url_pilis))
        # self.inermis_data = pd.read_csv(self.convert_google_sheet_url(gsheet_url_inermis))
        self.pilis_data = pd.read_csv(self.convert_google_sheet_url(result["pilis_tick"]))
        self.inermis_data = pd.read_csv(self.convert_google_sheet_url(result["winter_tick"]))

        # Load Lyme disease data (monthly and yearly)
        self.lyme_m, self.lyme_y = self.lyme_loader(links=result)
        (self.piliscs_2002_2023, self.piliscs_2024,
         self.pilissz_2020_2023, self.pilissz_2024) = self.rainfall_loader(links=result)

    def lyme_loader(self, links: dict) -> Tuple[pd.Series, pd.Series]:
        """
        Loads the Lyme disease data from Google Drive, both monthly and yearly data.

        :return: Tuple containing two pd.Series: monthly and yearly Lyme disease data.
        """
        # Google Drive downloader for monthly and yearly Lyme disease data
        g_dl_month = GoogleDataDownloader(
            file_url=links["lyme_month"],
            file_name="lyme_disease_monthly.csv")
        g_dl_year = GoogleDataDownloader(
            file_url=links["lyme_year"],
            file_name="lyme_disease_yearly.csv")

        # Load the data into pd.Series objects for monthly and yearly cases
        lyme_m = self.load_lyme_data(path=g_dl_month.file_path, period='M')
        lyme_y = self.load_lyme_data(path=g_dl_year.file_path, period='Y')

        return lyme_m, lyme_y

    def rainfall_loader(self, links: dict) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        g_dl_piliscsaba_2002_2023 = GoogleDataDownloader(
            file_url=links["piliscsaba_csapadek_2002-2023"],
            file_name="piliscsaba_2002-2023.csv"
        )
        g_dl_piliscsaba_2024 = GoogleDataDownloader(
            file_url=links["piliscsaba_csapadek_2024"],
            file_name="piliscsaba_csapadek_2024.csv"
        )

        g_dl_pilisszentkereszt_2020_2023 = GoogleDataDownloader(
            file_url=links["pilisszentkereszt_csapadek_2020-2023"],
            file_name="pilisszentkereszt_csapadek_2020-2023"
        )
        g_dl_pilisszentkereszt_2024 = GoogleDataDownloader(
            file_url=links["pilisszentkereszt_csapadek_2024"],
            file_name="pilisszentkereszt_csapadek_2024.csv"
        )

        piliscsaba_2002_2023 = self.load_rainfall_data(path=g_dl_piliscsaba_2002_2023.file_path)
        pilissaba_2024 = self.load_rainfall_data(path=g_dl_piliscsaba_2024.file_path)

        pilisszentkereszt_2020_2023 = self.load_rainfall_data(path=g_dl_pilisszentkereszt_2020_2023.file_path)
        pilisszentkereszt_2024 = self.load_rainfall_data(path=g_dl_pilisszentkereszt_2024.file_path)

        return piliscsaba_2002_2023, pilissaba_2024, pilisszentkereszt_2020_2023, pilisszentkereszt_2024

    @staticmethod
    def load_lyme_data(path, period: str) -> pd.Series:
        """
        Loads Lyme disease data from a CSV file, formats the date and converts it into a Series.

        :param path: Path to the CSV file containing Lyme disease data.
        :param period: The period type for the data ('M' for monthly, 'Y' for yearly).
        :return: A pandas Series indexed by the specified time period.
        """
        # Load the data into a DataFrame
        lyme_data = pd.read_csv(path)

        # Determine the time format based on the period type (monthly or yearly)
        time_format = None
        if period == 'Y':
            time_format = '%Y'
        if period == 'M':
            time_format = '%Y-%m'

        # Convert the 'Date' column to a datetime object and set it as index
        lyme_data['Date'] = pd.to_datetime(lyme_data['Date'], format=time_format)
        lyme_data.set_index(keys='Date', inplace=True)

        # Convert the DataFrame index to a period index (e.g., monthly or yearly)
        lyme_data = lyme_data.to_period(period)

        # Return the data as a Series
        lyme_series = pd.Series(index=lyme_data.index, data=lyme_data['Values'])

        return lyme_series

    @staticmethod
    def load_rainfall_data(path) -> pd.Series:
        rainfall_data = pd.read_csv(path, sep=';', header=4)

        # Removing unnecessary whitespaces from the columns
        rainfall_data.columns = rainfall_data.columns.str.strip()

        # Creating time index
        rainfall_data['Time'] = pd.to_datetime(rainfall_data["Time"], format='%Y%m%d')
        rainfall_data.set_index('Time', inplace=True)

        # Replacing missing values with NaN
        rainfall_data.replace(-999, np.nan, inplace=True)

        # Creating series to return
        rainfall_series = rainfall_data['r'].astype(float)

        return rainfall_series

    @staticmethod
    def convert_google_sheet_url(url: str) -> str:
        """
        Converts a Google Sheets URL into a CSV export URL.

        :param url: The original Google Sheets URL.
        :return: A modified URL that allows downloading the sheet as a CSV file.
        """
        # Regular expression to match and extract the necessary parts from the URL
        pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(?:/.*?gid=(\d+))?.*'

        # Replacement function to create the new CSV download URL
        def replacement(match):
            spreadsheet_id = match.group(1)
            gid = match.group(2) if match.group(2) else '0'  # Default gid to 0 if not provided
            return f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}'

        # Apply the replacement function to the input URL
        new_url = re.sub(pattern, replacement, url)

        return new_url
