"""
Gráf létrehozása
"""
import networkx as nx
import pandas as pd

from nlhs_tick_data_hungary.graph.graph_preparation.general_graph_preprocessor import GeneralGraphPreprocessor
from nlhs_tick_data_hungary.graph.graph_preparation.cooccurence_graph_preprocessor import CooccurenceGraphPreprocessor


class GraphCreator:
    """
    Class for creating a graph representation of the winter tick data.
    """

    # TODO: df-nél jobb név
    # TODO: leírni docstringbe, hogy ez a df, már a kiválasztott baktériumokat tartalmazó táblázatot kapja meg
    # TODO: átírni az összes docstring-et
    def __init__(self, df: pd.DataFrame, type_of_data: str, percentage: bool,
                 year: str, month: str,
                 type_of_graph: str):
        """
        Initialize the GraphPreProcessor with the specified parameters.

        Parameters:
        - tipus (str): The type of data to process (e.g., 'Nőstények', 'Hímek', 'Összes', etc.).
        - percentage (bool): Flag indicating whether to apply percentage calculations.
        - year (str): The year for which to process data (e.g., '2023').
        - month (str): The month for which to process data (e.g., 'January').
        - winter_tick (LoadWinterTickData): An instance of LoadWinterTickData for loading data.
        """
        self.df = df
        self.type_of_data = type_of_data
        self.percentage = percentage
        self.year = year
        self.month = month
        self.type_of_graph = type_of_graph

        self.processed_df = None  # Dataframe to store processed data
        self.G = None  # Graph object

    # TODO: png név colab-ba

    def run(self):
        """
        Execute the full processing pipeline: generate PNG name, load data, apply percentage, and create the
        graph.
        """
        # TODO: jobb név
        self._get_df_to_convert_to_graph()
        self.create_graph()  # Construct the graph from the processed data

    # TODO: nem megfeledkezni a weightmultiplier-ökről

    def _get_df_to_convert_to_graph(self):
        if self.type_of_graph == 'SparCC':
            preprocessor = GeneralGraphPreprocessor(df=self.df,
                                                    to_type=self.type_of_data,
                                                    year=self.year,
                                                    month=self.month)
            self.processed_df = preprocessor.preprocessed_df
        elif self.type_of_graph == 'Cooccurrence network':
            preprocessor = CooccurenceGraphPreprocessor(df=self.df,
                                                        type_of_data=self.type_of_data,
                                                        percentage=self.percentage,
                                                        year=self.year,
                                                        month=self.month)
            self.processed_df = preprocessor.preprocessed_df

    def create_graph(self):
        """
        Construct a graph using NetworkX from the processed data stored in my_df_s.
        """
        self.G = nx.Graph()  # Initialize a new graph

        # Add nodes to the graph for each bacterium
        for bacterium in self.processed_df.columns:
            self.G.add_node(bacterium)

        # Add edges between nodes based on the DataFrame's values
        for i in range(self.processed_df.shape[0]):
            for j in range(0, i):  # Only consider lower triangle to avoid duplicate edges
                weight = self.processed_df.iloc[i, j]
                if weight != 0:  # Only add edges with non-zero weights
                    self.G.add_edge(self.processed_df.index[i], self.processed_df.columns[j], weight=weight)
