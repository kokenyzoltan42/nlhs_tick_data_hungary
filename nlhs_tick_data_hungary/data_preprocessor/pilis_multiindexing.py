import pandas as pd


class PilisMultiindexing:
    def __init__(self, data):
        self.data = data

        self.tick_summary = None

        self.transform_to_multiindex()
        self.create_tick_summary()

    def transform_to_multiindex(self):
        multi_index = pd.MultiIndex.from_tuples([
            ('Eredeti csövek száma', '', ''),
            ('Válogatott csövek száma', '', ''),
            ('Gyűjtés időtartama (h)', '', ''),
            ('Gyűjtők száma', '', ''),
            ('Összes kullancs (db)', '', ''),
            ('I.', 'ricinus', 'nőstény'), ('I.', 'ricinus', 'hím'),
            ('I.', 'ricinus', 'nimfa'), ('I.', 'ricinus', 'lárva'),
            ('H.', 'inermis', 'nőstény'), ('H.', 'inermis', 'hím'),
            ('H.', 'inermis', 'nimfa'),
            ('H.', 'concinna', 'nőstény'), ('H.', 'concinna', 'hím'),
            ('H.', 'concinna', 'nimfa'), ('H.', 'concinna', 'lárva'),
            ('D.', 'marginatus', 'nőstény'), ('D.', 'marginatus', 'hím'),
            ('D.', 'marginatus', 'nimfa'), ('D.', 'marginatus', 'lárva'),
            ('D.', 'reticulatus', 'nőstény'), ('D.', 'reticulatus', 'hím'),
            ('D.', 'reticulatus', 'nimfa'), ('D.', 'reticulatus', 'lárva'),
            ('Min - T (°C)', '', ''),
            ('Max - T (°C)', '', ''),
            ('Min - RH(%)', '', ''),
            ('Max - RH(%)', '', ''),
            ('Normált gyűjtött kullancsok', '', '')
        ])

        df_multiindex = pd.DataFrame(columns=multi_index)

        df_multiindex[('Eredeti csövek száma', '', '')] = self.data['Eredeti csövek száma']
        df_multiindex[('Válogatott csövek száma', '', '')] = self.data['Válogatott csövek száma']
        df_multiindex[('Gyűjtés időtartama (h)', '', '')] = self.data['Gyűjtés időtartama (h)']
        df_multiindex[('Gyűjtők száma', '', '')] = self.data['Gyűjtők száma']
        df_multiindex[('Összes kullancs (db)', '', '')] = self.data['Összes kullancs (db)']

        for stage in ['nőstény', 'hím', 'nimfa']:
            df_multiindex[('I.', 'ricinus', stage)] = self.data[f'I. ricinus {stage}']
        df_multiindex[('I.', 'ricinus', 'lárva')] = self.data[f'I. lárva']

        for stage in ['nőstény', 'hím', 'nimfa']:
            df_multiindex[('H.', 'inermis', stage)] = self.data[f'H. inermis {stage}']
            df_multiindex[('H.', 'concinna', stage)] = self.data[f'H. concinna {stage}']
        df_multiindex[('H.', 'concinna', 'lárva')] = self.data[f'H. lárva']

        for species in ['marginatus', 'reticulatus']:
            for stage in ['nőstény', 'hím', 'nimfa', 'lárva']:
                df_multiindex[('D.', species, stage)] = self.data[f'D. {species} {stage}']

        df_multiindex[('Min - T (°C)', '', '')] = self.data['Min - T (°C)']
        df_multiindex[('Max - T (°C)', '', '')] = self.data['Max - T (°C)']
        df_multiindex[('Min - RH(%)', '', '')] = self.data['Min - RH(%)']
        df_multiindex[('Max - RH(%)', '', '')] = self.data['Max - RH(%)']
        df_multiindex[('Normált gyűjtött kullancsok', '', '')] = self.data['Normált gyűjtött kullancsok']

        self.data = df_multiindex

    def create_tick_summary(self):
        tick_species = [('I.', 'ricinus'), ('H.', 'inermis'), ('H.', 'concinna'), ('D.', 'marginatus'),
                        ('D.', 'reticulatus')]
        df_summary = pd.DataFrame()

        for species in tick_species:
            states_columns = [(f'{species[0]}', f'{species[1]}', state) for state in
                              ['nőstény', 'hím', 'nimfa', 'lárva']]

            try:
                df_summary[f'{species[0]} {species[1]}'] = self.data[states_columns].sum(axis=1)
            except:
                df_summary[f'{species[0]} {species[1]}'] = self.data[
                    [col for col in states_columns if col in self.data.columns]].sum(axis=1)

        self.tick_summary = df_summary
