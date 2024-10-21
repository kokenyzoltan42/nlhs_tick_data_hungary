import pandas as pd


class PilisMultiindexing:
    def __init__(self, data):
        self.data = data
        self.tick_summary = None

        self.transform_to_multiindex()
        self.create_tick_summary()

    def _create_multiindex_structure(self):
        # Definiáljuk a MultiIndex felépítését egy struktúrával, ami a metódus elejére kerül
        multi_index_columns = [
            ('Eredeti csövek száma', '', ''), ('Válogatott csövek száma', '', ''), ('Gyűjtés időtartama (h)', '', ''),
            ('Gyűjtők száma', '', ''), ('Összes kullancs (db)', '', ''),
            # I. ricinus fajok
            ('I.', 'ricinus', 'nőstény'), ('I.', 'ricinus', 'hím'), ('I.', 'ricinus', 'nimfa'),
            ('I.', 'ricinus', 'lárva'),
            # H. inermis és H. concinna fajok
            ('H.', 'inermis', 'nőstény'), ('H.', 'inermis', 'hím'), ('H.', 'inermis', 'nimfa'),
            ('H.', 'concinna', 'nőstény'), ('H.', 'concinna', 'hím'), ('H.', 'concinna', 'nimfa'),
            ('H.', 'concinna', 'lárva'),
            # D. marginatus és D. reticulatus fajok
            ('D.', 'marginatus', 'nőstény'), ('D.', 'marginatus', 'hím'), ('D.', 'marginatus', 'nimfa'),
            ('D.', 'marginatus', 'lárva'),
            ('D.', 'reticulatus', 'nőstény'), ('D.', 'reticulatus', 'hím'), ('D.', 'reticulatus', 'nimfa'),
            ('D.', 'reticulatus', 'lárva'),
            # Egyéb adatok
            ('Min - T (°C)', '', ''), ('Max - T (°C)', '', ''), ('Min - RH(%)', '', ''), ('Max - RH(%)', '', ''),
            ('Normált gyűjtött kullancsok', '', '')
        ]
        return pd.MultiIndex.from_tuples(multi_index_columns)

    def _populate_dataframe(self, df_multiindex, column_tuples, data_mapping):
        for multiindex_col, data_col in data_mapping.items():
            df_multiindex[multiindex_col] = self.data[data_col]

    def transform_to_multiindex(self):
        multi_index = self._create_multiindex_structure()
        df_multiindex = pd.DataFrame(columns=multi_index)

        # Alapvető adatok kitöltése
        base_data_mapping = {
            ('Eredeti csövek száma', '', ''): 'Eredeti csövek száma',
            ('Válogatott csövek száma', '', ''): 'Válogatott csövek száma',
            ('Gyűjtés időtartama (h)', '', ''): 'Gyűjtés időtartama (h)',
            ('Gyűjtők száma', '', ''): 'Gyűjtők száma',
            ('Összes kullancs (db)', '', ''): 'Összes kullancs (db)'
        }
        self._populate_dataframe(df_multiindex, base_data_mapping.keys(), base_data_mapping)

        # Tick fajok és stádiumok kitöltése
        tick_stages = ['nőstény', 'hím', 'nimfa', 'lárva']

        # I. ricinus kitöltése
        for stage in tick_stages[:-1]:  # Az utolsó a 'lárva'
            df_multiindex[('I.', 'ricinus', stage)] = self.data[f'I. ricinus {stage}']
        df_multiindex[('I.', 'ricinus', 'lárva')] = self.data[f'I. lárva']

        # H. inermis és H. concinna kitöltése
        for species in ['inermis', 'concinna']:
            for stage in tick_stages:
                col_key = ('H.', species, stage)
                data_key = f'H. {species} {stage}' if stage != 'lárva' else f'H. lárva'
                df_multiindex[col_key] = self.data[data_key]

        # D. marginatus és D. reticulatus kitöltése
        for species in ['marginatus', 'reticulatus']:
            for stage in tick_stages:
                df_multiindex[('D.', species, stage)] = self.data[f'D. {species} {stage}']

        # Egyéb adatok kitöltése
        weather_data_mapping = {
            ('Min - T (°C)', '', ''): 'Min - T (°C)',
            ('Max - T (°C)', '', ''): 'Max - T (°C)',
            ('Min - RH(%)', '', ''): 'Min - RH(%)',
            ('Max - RH(%)', '', ''): 'Max - RH(%)',
            ('Normált gyűjtött kullancsok', '', ''): 'Normált gyűjtött kullancsok'
        }
        self._populate_dataframe(df_multiindex, weather_data_mapping.keys(), weather_data_mapping)

        self.data = df_multiindex

    def _sum_species_data(self, species, stages):
        """Helper function to sum data for a specific species and its life stages."""
        columns = [(species[0], species[1], stage) for stage in stages]
        # Csak azok az oszlopok kerülnek összesítésre, amelyek ténylegesen léteznek a DataFrame-ben
        valid_columns = [col for col in columns if col in self.data.columns]
        if valid_columns:
            return self.data[valid_columns].sum(axis=1)
        return pd.Series(index=self.data.index, data=0)  # Ha nincs érvényes adat, nulla sorozatot ad vissza

    def create_tick_summary(self):
        tick_species = [('I.', 'ricinus'), ('H.', 'inermis'), ('H.', 'concinna'), ('D.', 'marginatus'),
                        ('D.', 'reticulatus')]
        tick_stages = ['nőstény', 'hím', 'nimfa', 'lárva']
        df_summary = pd.DataFrame()

        for species in tick_species:
            species_label = f'{species[0]} {species[1]}'
            df_summary[species_label] = self._sum_species_data(species, tick_stages)

        self.tick_summary = df_summary
