import json
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

    def __init__(self  # ,
                 # gsheet_url_pilis: str,
                 # gsheet_url_inermis: str
                 ):
        """
        Initializes the GoogleDriveDataloader with URLs and loads the data from the given Google Sheets.

        :param gsheet_url_pilis: URL of the Google Sheet for Pilis tick data.
        :param gsheet_url_inermis: URL of the Google Sheet for Inermis tick data.
        """

        # Load data from Google Sheets as CSV
        with open(url_path + f'/links.json', 'r+') as file:
            result = json.load(file)
        # self.pilis_data = pd.read_csv(self.convert_google_sheet_url(gsheet_url_pilis))
        # self.inermis_data = pd.read_csv(self.convert_google_sheet_url(gsheet_url_inermis))
        self.pilis_data = pd.read_csv(self.convert_google_sheet_url(result["pilis_tick"]))
        self.inermis_data = pd.read_csv(self.convert_google_sheet_url(result["winter_tick"]))

        # Load Lyme disease data (monthly and yearly)
        self.lyme_m, self.lyme_y = self.lyme_loader()

    def lyme_loader(self):
        """
        Loads the Lyme disease data from Google Drive, both monthly and yearly data.

        :return: Tuple containing two pd.Series: monthly and yearly Lyme disease data.
        """
        # Google Drive downloader for monthly and yearly Lyme disease data
        g_dl_month = GoogleDataDownloader(
            file_url="https://drive.google.com/file/d/12Z8fxqLuTHwhSKpNUidTQYPXb5BG_O_s/view?usp=sharing",
            file_name="lyme_disease_monthly.csv")
        g_dl_year = GoogleDataDownloader(
            file_url="https://drive.google.com/file/d/1V4ShcC6lOfAatkru243visXWXSU3tgER/view?usp=sharing",
            file_name="lyme_disease_yearly.csv")

        # Load the data into pd.Series objects for monthly and yearly cases
        lyme_m = self.load_lyme_data(path=g_dl_month.file_path, period='M')
        lyme_y = self.load_lyme_data(path=g_dl_year.file_path, period='Y')

        return lyme_m, lyme_y

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
