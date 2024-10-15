import numpy as np
import pandas as pd
import re


class PilisPreprocessor:
    def __init__(self, data, remove_reds: bool = True):
        self.data = data
        self.remove_reds = remove_reds

        self.adjust_columns()
        self.split_temps_and_rhs()
        self.remove_reds_from_table()
        self.fill_missing_data()
        self.adjust_indices()
        self.normalize_tick_gathering()

    @staticmethod
    def split_min_max(temp):
        temp = str(temp).replace(',', '.').strip()
        if re.match(pattern=r"^\s*\d+([.,]\d+)?\s*$", string=temp):
            # Ha csak egy szám van
            min_val = max_val = float(temp)
            return pd.Series([min_val, max_val])
        elif re.match(pattern=r"^\s*\d+([.,]\d+)?\s*-\s*\d+([.,]\d+)?\s*$", string=temp):
            # Ha intervallum van
            min_val, max_val = map(float, temp.split('-'))
            return pd.Series([min_val, max_val])
        else:
            return pd.Series([None, None])

    @staticmethod
    def adjust_months(df):
        prev_month = None
        for idx, row in df.iterrows():
            if prev_month == row['Date']:
                df.at[idx - 1, 'Date'] -= 1
            prev_month = row['Date']
        return df

    def adjust_columns(self):
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

        self.data = self.data.drop(index=0).reset_index().drop(columns="index")

        columns_to_float = [
            'I. ricinus hím', 'I. ricinus nőstény', 'I. ricinus nimfa', 'I. lárva',
            'H. inermis nőstény', 'H. inermis hím', 'H. inermis nimfa',
            'H. concinna nőstény', 'H. concinna hím', 'H. concinna nimfa', 'H. lárva',
            'D. marginatus nőstény', 'D. marginatus hím', 'D. marginatus nimfa', 'D. marginatus lárva',
            'D. reticulatus nőstény', 'D. reticulatus hím', 'D. reticulatus nimfa', 'D. reticulatus lárva',
            'Gyűjtők száma', 'Összes kullancs (db)'
        ]

        self.data[columns_to_float] = self.data[columns_to_float].astype(float)
        self.data["Gyűjtés időtartama (h)"] = self.data["Gyűjtés időtartama (h)"].str.replace(',', '.').astype(float)

    def split_temps_and_rhs(self):
        self.data[['Min - T (°C)', 'Max - T (°C)']] = self.data['T (°C)'].apply(self.split_min_max)
        self.data[['Min - RH(%)', 'Max - RH(%)']] = self.data['RH(%)'].apply(self.split_min_max)

        self.data.drop(columns=['T (°C)', 'RH(%)'], inplace=True)

    def remove_reds_from_table(self):
        if self.remove_reds:
            datumok = ['2015-05-13', '2015-06-05', '2015-07-01', '2016-06-22']
            self.data = self.data[~self.data['Gyűjtési dátum'].isin(datumok)]

            self.data.reset_index(drop=True, inplace=True)

    def fill_missing_data(self):
        self.data = self.data.fillna(np.nan)
        self.data['Gyűjtők száma'] = self.data['Gyűjtők száma'].fillna(self.data['Eredeti csövek száma'])

    def adjust_indices(self):
        self.data['Date'] = pd.to_datetime(self.data['Gyűjtési dátum']).dt.to_period('M')

        self.data = self.adjust_months(self.data)

        avg_cols = {
            'Min - T (°C)': 'mean',
            'Max - T (°C)': 'mean',
            'Min - RH(%)': 'mean',
            'Max - RH(%)': 'mean',
        }

        string_cols = ['Gyűjtés helye', 'Gyűjtési dátum', 'Egyéb megjegyzés']

        df_grouped = self.data.groupby('Date').agg(avg_cols).reset_index()

        for col in self.data.columns:
            if col not in avg_cols.keys() and col != 'Date' and col not in string_cols:
                df_grouped[col] = self.data.groupby('Date')[col].sum().values
                df_grouped[col] = df_grouped[col].replace(0, np.nan)
            if col in string_cols:
                df_grouped[col] = self.data[col]

        df_grouped = df_grouped.set_index('Date')
        df_grouped = df_grouped.drop(columns='Gyűjtési dátum')
        self.data = df_grouped

        full_index = pd.date_range(start='2011-03', end='2024-08', freq='M').to_period('M')
        self.data = self.data.reindex(full_index, fill_value=np.nan)

    def normalize_tick_gathering(self):
        self.data['Normált gyűjtött kullancsok'] = self.data['Összes kullancs (db)'] / self.data['Gyűjtők száma']

    def handling_missing_data(self):
        pass
