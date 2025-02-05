import re

import pandas as pd


class GoogleSheetDataLoader:
    """
    Class for loading data from Google Sheets.
    """
    def __init__(self, url: str):
        self.url = url

    def load_data(self) -> pd.DataFrame:
        """
        Loads the data from a Google Sheet.
        :return pd.DataFrame: Returns a pandas dataframe containing the data.
        """
        return pd.read_csv(self.convert_google_sheet_url(self.url))

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
