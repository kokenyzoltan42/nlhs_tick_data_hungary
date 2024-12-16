import networkx as nx
import numpy as np

from nlhs_tick_data_hungary.data_preprocessor.winter_tick.load_winter_tick_data import LoadWinterTickData
from nlhs_tick_data_hungary.utils.assisting_methods import AssistingMethods


class GraphPreProcessor:
    """
    Class for creating a graph representation of the winter tick data.
    """
    def __init__(self, tipus: str, percentage: bool,
                 year: str, month: str, winter_tick: LoadWinterTickData):
        """
        Initialize the GraphPreProcessor with the specified parameters.

        Parameters:
        - tipus (str): The type of data to process (e.g., 'Nőstények', 'Hímek', 'Összes', etc.).
        - percentage (bool): Flag indicating whether to apply percentage calculations.
        - year (str): The year for which to process data (e.g., '2023').
        - month (str): The month for which to process data (e.g., 'January').
        - winter_tick (LoadWinterTickData): An instance of LoadWinterTickData for loading data.
        """
        self.tipus = tipus
        self.percentage = percentage
        self.year = year
        self.month = month

        self.weight_multiplier = 15  # Default multiplier for edge weights
        self.epsilon = 1e-5  # Small value to prevent division by zero

        self.my_df_s = None  # Dataframe to store processed data
        self.instances = None  # Number of instances for calculations
        self.G = None  # Graph object

        self.png_name = None  # Name for the output PNG file

        self.winter_tick = winter_tick  # Instance to load tick data

    def run(self):
        """
        Execute the full processing pipeline: generate PNG name, load data, apply percentage, and create the
        graph.
        """
        self._create_png_name()  # Generate output filename based on parameters
        self._get_data()  # Load data based on type
        self._apply_percentage()  # Convert values to percentages if required
        self.create_graph()  # Construct the graph from the processed data

    def _create_png_name(self):
        """
        Generate the name for the output PNG file based on specified parameters.
        """
        if self.percentage:
            szazalek = '_%'
        else:
            szazalek = '_'

        if self.year == '':
            selected_year = '_osszes_ev'
        else:
            selected_year = '_' + self.year
        if self.month == '':
            selected_month = '_osszes_honap'
        else:
            selected_month = '_' + self.month

        if self.winter_tick.preprocessor.selected_group == '':
            selected_group = 'nincs_csoport_'
        else:
            selected_group = self.winter_tick.preprocessor.selected_group + '_'

        # Create the PNG filename
        self.png_name = 'Halozat_' + selected_group + self.tipus + szazalek + selected_year + selected_month

    def _get_data(self):
        """
        Load the tick data based on the specified type and store it in the my_df_s attribute.

        The method distinguishes between female, male, and combined data types,
        as well as calculations for differences between sexes when applicable.
        """
        if self.tipus == 'Nőstények':
            # Load data for females
            temp_df = self.winter_tick.run(gender='Female', year=self.year, month=self.month).astype(int)
            self.instances = len(temp_df.columns)
            self.my_df_s = AssistingMethods.create_crosstable(df=temp_df)

        elif self.tipus == 'Hímek':
            # Load data for males
            temp_df = self.winter_tick.run(gender='Male', year=self.year, month=self.month).astype(int)
            self.instances = len(temp_df.columns)
            self.my_df_s = AssistingMethods.create_crosstable(df=temp_df)

        elif self.tipus == 'Összes':
            # Load data for all
            temp_df = self.winter_tick.run(gender='All', year=self.year, month=self.month).astype(int)
            self.instances = len(temp_df.columns)
            self.my_df_s = AssistingMethods.create_crosstable(df=temp_df)

        elif self.tipus in ['Különbség', 'Nőstény - Hím', 'Hím - Nőstény']:
            # Load data for both genders to calculate differences
            fem_df = self.winter_tick.run(gender='Female', year=self.year, month=self.month).astype(int)
            male_df = self.winter_tick.run(gender='Male', year=self.year, month=self.month).astype(int)

            # Create crosstables for each gender
            fem_crosstable = AssistingMethods.create_crosstable(fem_df).fillna(0)
            male_crosstable = AssistingMethods.create_crosstable(male_df).fillna(0)

            # Calculate differences based on the specified type
            if self.tipus == 'Nőstény - Hím':
                self.my_df_s = fem_crosstable - male_crosstable
            elif self.tipus == 'Hím - Nőstény':
                self.my_df_s = male_crosstable - fem_crosstable
            elif self.tipus == 'Különbség':
                self.my_df_s = abs(male_crosstable - fem_crosstable)

            if self.percentage:
                # Convert crosstables to percentages
                fem_crosstable = fem_crosstable / len(fem_df.columns) * 100
                male_crosstable = male_crosstable / len(male_df.columns) * 100
                # Calculate log differences if necessary
                if self.tipus == 'Hím - Nőstény':
                    self.my_df_s = np.log((male_crosstable + self.epsilon) / (fem_crosstable + self.epsilon))
                elif self.tipus == 'Nőstény - Hím':
                    self.my_df_s = np.log((fem_crosstable + self.epsilon) / (male_crosstable + self.epsilon))
                elif self.tipus == 'Különbség':
                    self.my_df_s = abs(np.log((male_crosstable + self.epsilon) / (fem_crosstable + self.epsilon)))
                self.instances = 1  # Set instances to 1 for percentage calculations

            # Adjust weight multiplier based on the type of analysis
            if self.tipus == 'Különbség':
                self.weight_multiplier = 6
            elif self.tipus in ['Nőstény - Hím', 'Hím - Nőstény']:
                self.weight_multiplier = 6

    def _apply_percentage(self):
        """
        Convert the processed data to percentage if the percentage flag is set.

        This method modifies my_df_s in place, converting counts to percentages based on the number of instances.
        """
        if self.percentage and self.tipus not in ['Különbség', 'Nőstény - Hím', 'Hím - Nőstény']:
            self.my_df_s = (self.my_df_s.fillna(0) / self.instances * 100).round().astype(int)
            self.my_df_s = self.my_df_s.astype(float)  # Ensure the DataFrame is in float format

    def create_graph(self):
        """
        Construct a graph using NetworkX from the processed data stored in my_df_s.
        """
        self.G = nx.Graph()  # Initialize a new graph

        # Add nodes to the graph for each bacterium
        for bacterium in self.my_df_s.columns:
            self.G.add_node(bacterium)

        # Add edges between nodes based on the DataFrame's values
        for i in range(self.my_df_s.shape[0]):
            for j in range(0, i):  # Only consider lower triangle to avoid duplicate edges
                weight = self.my_df_s.iloc[i, j]
                if weight != 0:  # Only add edges with non-zero weights
                    self.G.add_edge(self.my_df_s.index[i], self.my_df_s.columns[j], weight=weight)
