import pandas as pd


class PilisMultiindexing:
    """
    This class is responsible for transforming the raw tick data from Pilisszentkereszt into a MultiIndex DataFrame
    and creating summary data for different tick species and their life stages.

    Attributes:
    ----------
    data : pd.DataFrame
        The original tick data.
    tick_summary : pd.DataFrame or None
        A summary DataFrame for different tick species and their life stages. Initialized as None.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initializes the PilisMultiindexing class with the provided raw tick data and transforms it into a
        MultiIndex structure. Also, it creates a summary of tick data by species and stages.

        :param data: Raw tick data as a pandas DataFrame.
        """
        self.data = data
        self.tick_summary = None

        # Transform the data into a MultiIndex structure upon initialization
        self.transform_to_multiindex()
        # Create a tick summary for different species
        self.create_tick_summary()

    @staticmethod
    def _create_multiindex_structure() -> pd.MultiIndex:
        """
        Create a MultiIndex structure for organizing the tick data with columns representing different species,
        life stages, and additional metadata like temperature and relative humidity (RH).

        :return: A pandas MultiIndex object defining the structure of the DataFrame columns.
        """
        # Define the MultiIndex structure for species, life stages, and additional data
        multi_index_columns = [
            ('Eredeti csövek száma', '', ''), ('Válogatott csövek száma', '', ''), ('Gyűjtés időtartama (h)', '', ''),
            ('Gyűjtők száma', '', ''), ('Összes kullancs (db)', '', ''),
            # I. ricinus species
            ('I.', 'ricinus', 'nőstény'), ('I.', 'ricinus', 'hím'), ('I.', 'ricinus', 'nimfa'),
            ('I.', 'ricinus', 'lárva'),
            # H. inermis and H. concinna species
            ('H.', 'inermis', 'nőstény'), ('H.', 'inermis', 'hím'), ('H.', 'inermis', 'nimfa'),
            ('H.', 'concinna', 'nőstény'), ('H.', 'concinna', 'hím'), ('H.', 'concinna', 'nimfa'),
            ('H.', 'concinna', 'lárva'),
            # D. marginatus and D. reticulatus species
            ('D.', 'marginatus', 'nőstény'), ('D.', 'marginatus', 'hím'), ('D.', 'marginatus', 'nimfa'),
            ('D.', 'marginatus', 'lárva'),
            ('D.', 'reticulatus', 'nőstény'), ('D.', 'reticulatus', 'hím'), ('D.', 'reticulatus', 'nimfa'),
            ('D.', 'reticulatus', 'lárva'),
            # Additional data (Temperature, RH)
            ('Min - T (°C)', '', ''), ('Max - T (°C)', '', ''), ('Min - RH(%)', '', ''), ('Max - RH(%)', '', ''),
            ('Normált gyűjtött kullancsok', '', '')
        ]
        # Return the constructed MultiIndex object
        return pd.MultiIndex.from_tuples(multi_index_columns)

    def _populate_dataframe(self, df_multiindex: pd.DataFrame, data_mapping: dict) -> None:
        """
        Populate the provided MultiIndex DataFrame with data from the original DataFrame.

        :param df_multiindex: The MultiIndex DataFrame to be populated.
        :param data_mapping: Dictionary mapping MultiIndex columns to the original DataFrame columns.
        """
        # Iterate over the mapping and populate each MultiIndex column with the corresponding data
        for multiindex_col, data_col in data_mapping.items():
            df_multiindex[multiindex_col] = self.data[data_col]

    def transform_to_multiindex(self) -> None:
        """
        Transforms the raw tick data into a MultiIndex DataFrame using species and life stages.
        This function also handles the additional metadata such as temperature, RH, and collection information.
        """
        # Create the MultiIndex structure for the DataFrame
        multi_index: pd.MultiIndex = self._create_multiindex_structure()
        df_multiindex: pd.DataFrame = pd.DataFrame(columns=multi_index)

        # Base data mapping (common columns)
        base_data_mapping = {
            ('Eredeti csövek száma', '', ''): 'Eredeti csövek száma',
            ('Válogatott csövek száma', '', ''): 'Válogatott csövek száma',
            ('Gyűjtés időtartama (h)', '', ''): 'Gyűjtés időtartama (h)',
            ('Gyűjtők száma', '', ''): 'Gyűjtők száma',
            ('Összes kullancs (db)', '', ''): 'Összes kullancs (db)'
        }
        # Populate the base columns
        self._populate_dataframe(df_multiindex=df_multiindex, data_mapping=base_data_mapping)

        # Tick stages to be filled for species
        tick_stages: list = ['nőstény', 'hím', 'nimfa', 'lárva']

        # Fill data for I. ricinus species
        for stage in tick_stages[:-1]:  # All stages except 'lárva'
            df_multiindex[('I.', 'ricinus', stage)] = self.data[f'I. ricinus {stage}']
        df_multiindex[('I.', 'ricinus', 'lárva')] = self.data[f'I. lárva']

        # Fill data for H. inermis and H. concinna species
        for species in ['inermis', 'concinna']:
            for stage in tick_stages:
                if not (species == 'inermis' and stage == 'lárva'):  # H. inermis has no 'lárva'
                    col_key = ('H.', species, stage)
                    data_key = f'H. {species} {stage}' if stage != 'lárva' else f'H. lárva'
                    df_multiindex[col_key] = self.data[data_key]

        # Fill data for D. marginatus and D. reticulatus species
        for species in ['marginatus', 'reticulatus']:
            for stage in tick_stages:
                df_multiindex[('D.', species, stage)] = self.data[f'D. {species} {stage}']

        # Additional weather and environment data
        weather_data_mapping: dict = {
            ('Min - T (°C)', '', ''): 'Min - T (°C)',
            ('Max - T (°C)', '', ''): 'Max - T (°C)',
            ('Min - RH(%)', '', ''): 'Min - RH(%)',
            ('Max - RH(%)', '', ''): 'Max - RH(%)',
            ('Normált gyűjtött kullancsok', '', ''): 'Normált gyűjtött kullancsok'
        }
        # Populate the additional data columns
        self._populate_dataframe(df_multiindex=df_multiindex, data_mapping=weather_data_mapping)

        # Assign the transformed MultiIndex DataFrame to the class attribute `data`
        self.data = df_multiindex

    def _sum_species_data(self, species: tuple, stages: list) -> pd.Series:
        """
        Helper function to sum data for a specific species and its life stages.

        :param species: A tuple representing the species (e.g., ('I.', 'ricinus')).
        :param stages: A list of life stages (e.g., ['nőstény', 'hím', 'nimfa', 'lárva']).
        :return: A pandas Series containing the summed data for the species across all stages.
        """
        # Create column names based on the species and stages
        columns: list = [(species[0], species[1], stage) for stage in stages]
        # Only sum columns that actually exist in the DataFrame
        valid_columns: list = [col for col in columns if col in self.data.columns]
        if valid_columns:
            return self.data[valid_columns].sum(axis=1)
        # Return a Series of zeros if no valid columns are found
        return pd.Series(index=self.data.index, data=0)

    def create_tick_summary(self) -> None:
        """
        Creates a summary DataFrame that contains the total counts for each tick species across all life stages.
        This summary aggregates data for I. ricinus, H. inermis, H. concinna, D. marginatus, and D. reticulatus.
        """
        # Define the species to be summarized
        tick_species: list = [('I.', 'ricinus'), ('H.', 'inermis'), ('H.', 'concinna'), ('D.', 'marginatus'),
                              ('D.', 'reticulatus')]
        # Define the life stages
        tick_stages: list = ['nőstény', 'hím', 'nimfa', 'lárva']
        df_summary: pd.DataFrame = pd.DataFrame()

        # Loop through each species and calculate the total for their stages
        for species in tick_species:
            species_label: str = f'{species[0]} {species[1]}'
            df_summary[species_label] = self._sum_species_data(species, tick_stages)

        # Assign the summary DataFrame to the class attribute `tick_summary`
        self.tick_summary = df_summary
