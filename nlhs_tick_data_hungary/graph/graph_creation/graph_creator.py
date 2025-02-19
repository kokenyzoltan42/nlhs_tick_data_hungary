import networkx as nx
import pandas as pd

from nlhs_tick_data_hungary.graph.graph_preparation.cooccurence_graph_preprocessor import CooccurenceGraphPreprocessor
from nlhs_tick_data_hungary.graph.graph_preparation.general_graph_preprocessor import GeneralGraphPreprocessor
from nlhs_tick_data_hungary.graph.graph_preparation.sparcc.SparCCRunner import SparCCRunner


class GraphCreator:
    """
    Class for creating a graph representation of the winter tick data.

    This class processes tick data, constructs either a SparCC-based graph or a co-occurrence network,
    and stores the result in a graph object.
    """
    def __init__(self,
                 df: pd.DataFrame,
                 type_of_data: str, convert_to_percentage: bool,
                 year: str, month: str,
                 type_of_graph: str,
                 sparcc_args: dict = None) -> None:
        """
        Initialize the GraphCreator with the specified parameters.

        :param pd.DataFrame df: The dataframe containing the data of the selected group of bacteria
        :param str type_of_data: The type of data to process (e.g., 'Nőstények', 'Hímek', 'Összes', etc.)
        :param bool convert_to_percentage: Whether to apply percentage transformations to the data
        :param str year: The year for which the data is being processed (e.g., '2023')
        :param str month: The month for which the data is being processed (e.g., 'January')
        :param str type_of_graph: The type of graph to create (e.g., 'SparCC', 'Cooccurrence network')
        :param dict sparcc_args: Arguments for SparCC algorithm (used only if type_of_graph is 'SparCC')
        """
        self.df = df
        self.type_of_data = type_of_data
        self.convert_to_percentage = convert_to_percentage
        self.year = year
        self.month = month
        self.type_of_graph = type_of_graph
        self.sparcc_args = sparcc_args

        self.final_table = None  # Dataframe to store processed data
        self.G = None  # Object to store created graph

    def run(self):
        """
        Execute the full data processing pipeline: convert data to a graph format, process data (e.g., SparCC or
        co-occurrence), and create the graph.
        """
        self.prepare_data_for_graph_creation()
        self.create_graph()

    def prepare_data_for_graph_creation(self):
        """
        Preprocess the input data based on the selected graph type and transform it into a format suitable for
        graph creation.
        """
        if self.type_of_graph == 'SparCC':
            # Preprocess data for SparCC
            preprocessor = GeneralGraphPreprocessor(df=self.df,
                                                    to_type=self.type_of_data,
                                                    year=self.year,
                                                    month=self.month)
            processed_df = preprocessor.preprocessed_df

            # Run SparCC algorithm on the preprocessed data
            sparcc = SparCCRunner(df=processed_df,
                                  args=self.sparcc_args)
            self.final_table = sparcc.run()

        elif self.type_of_graph == 'Cooccurrence network':
            # Preprocess data for co-occurrence network
            preprocessor = CooccurenceGraphPreprocessor(df=self.df,
                                                        type_of_data=self.type_of_data,
                                                        convert_to_percentage=self.convert_to_percentage,
                                                        year=self.year,
                                                        month=self.month)
            preprocessor.run()
            self.final_table = preprocessor.preprocessed_df

    def create_graph(self):
        """
        Construct a graph based on the processed data stored in `final_table`.

        Nodes represent bacteria, and edges are weighted based on the values in `final_table`.
        Only non-zero values are used to create edges.
        """
        self.G = nx.Graph()

        # Add nodes to the graph for each bacterium
        for bacterium in self.final_table.columns:
            self.G.add_node(bacterium)

        # Add edges between nodes with weight based on the DataFrame's values
        for i in range(self.final_table.shape[0]):
            for j in range(0, i):  # Only consider lower triangle to avoid duplicate edges
                weight = self.final_table.iloc[i, j]
                if weight != 0:  # Only add edges with non-zero weights
                    self.G.add_edge(self.final_table.index[i], self.final_table.columns[j], weight=weight)
