import pandas as pd
import re

from nlhs_tick_data_hungary.data_loading.GoogleDataDownLoader import GoogleDataDownloader


class DataLoader:
    def __init__(self, gsheet_url_pilis, gsheet_url_inermis):
        self.gsheet_url_pilis = gsheet_url_pilis
        self.gsheet_url_inermis = gsheet_url_inermis

        self.pilis_data = pd.read_csv(self.convert_google_sheet_url(gsheet_url_pilis))
        self.inermis_data = pd.read_csv(self.convert_google_sheet_url(gsheet_url_inermis))

        self.lyme_m, self.lyme_y = self.lyme_loader()

    @staticmethod
    def lyme_loader():
        g_dl_month = GoogleDataDownloader(
            file_url="https://drive.google.com/file/d/12Z8fxqLuTHwhSKpNUidTQYPXb5BG_O_s/view?usp=sharing",
            file_name="lyme_disease_monthly.csv")
        g_dl_year = GoogleDataDownloader(
            file_url="https://drive.google.com/file/d/1V4ShcC6lOfAatkru243visXWXSU3tgER/view?usp=sharing",
            file_name="lyme_disease_yearly.csv")

        lyme_monthly = pd.read_csv(g_dl_month.file_path)
        lyme_year = pd.read_csv(g_dl_year.file_path)

        lyme_monthly['Date'] = pd.to_datetime(lyme_monthly['Date'], format='%Y-%m')
        lyme_year['Date'] = pd.to_datetime(lyme_year['Date'], format='%Y')

        lyme_monthly.set_index('Date', inplace=True)
        lyme_year.set_index('Date', inplace=True)

        lyme_monthly = lyme_monthly.to_period('M')
        lyme_year = lyme_year.to_period('Y')

        lyme_m = pd.Series(index=lyme_monthly.index, data=lyme_monthly['Values'])
        lyme_y = pd.Series(index=lyme_year.index, data=lyme_year['Values'])

        return lyme_m, lyme_y

    @staticmethod
    def convert_google_sheet_url(url):
        # Regular expression to match the necessary part of the URL
        pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(?:/.*?gid=(\d+))?.*'

        # Replace function to construct the new URL for CSV export
        def replacement(match):
            spreadsheet_id = match.group(1)
            gid = match.group(2) if match.group(2) else '0'  # Default gid to 0 if not provided
            return f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}'

        # Apply the replacement to the input URL
        new_url = re.sub(pattern, replacement, url)

        return new_url
