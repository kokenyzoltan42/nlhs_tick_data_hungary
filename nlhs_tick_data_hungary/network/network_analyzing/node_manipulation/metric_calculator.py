import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing import NetworkAnalyzer


class MetricCalculator:
    """
    A utility class for calculating various network metrics.

    This class provides static methods that interface with the `NetworkAnalyzer` class to compute:
      - The size of the largest connected component (LCC).
      - The connectivity loss between two LCC measurements.
      - A selected node defending metric (e.g., average path length or LCC size).
      - Node centrality metrics such as betweenness or degree centrality.
    """

    @staticmethod
    def calc_lcc(network: nx.Graph) -> int:
        """
        Calculate the size of the largest connected component (LCC) in the network.

        :param nx.Graph network: A networkx Graph object for which the LCC size is to be calculated.
        :return int: The number of nodes in the largest connected component as an integer.
        """
        analyzer = NetworkAnalyzer(config={}, network=network)
        return analyzer.calc_size_of_largest_connected_component()

    @staticmethod
    def calc_connectivity_loss(initial_lcc: int, current_lcc: int) -> float:
        """
        Calculate the connectivity loss given the initial and current largest connected component sizes.
        The connectivity loss is defined as the relative decrease in the size of the LCC.

        :param int initial_lcc: The size of the largest connected component before any change.
        :param int current_lcc: The current size of the largest connected component.
        :return float: The connectivity loss as a float (value between 0 and 1).
        """
        return (initial_lcc - current_lcc) / initial_lcc

    @staticmethod
    def calc_node_defending_metric(network: nx.Graph, metric: str) -> float:
        """
        Calculate a network defending metric for the provided network.
        The metric to calculate is determined by the 'defending_metric' parameter and can be one of the following:
          - 'APL': Average path length of the network.
          - 'LCC': Size of the largest connected component.

        :param nx.Graph network: A networkx Graph object for which the metric is to be calculated.
        :param str metric: A string key ('APL' or 'LCC') specifying the metric type.
        :return float: The computed metric value. This can be an integer (for LCC) or a float (for APL).
        """
        analyzer = NetworkAnalyzer(config={}, network=network)
        metric_methods = {
            'APL': analyzer.calc_average_path_length,
            'LCC': analyzer.calc_size_of_largest_connected_component
        }
        return metric_methods[metric]()

    @staticmethod
    def calc_centrality(network: nx.Graph, centrality_measure: str) -> dict:
        """
        Calculate the node centrality of the network based on the specified centrality measure.

        Supported centrality measures include:
          - 'betweenness'
          - 'degree'

        :param nx.Graph network: A networkx Graph object for which the centrality measure is to be computed.
        :param str centrality_measure: A string key ('betweenness' or 'degree') specifying the centrality type.
        :return dict: A dictionary mapping each node to its computed centrality value.
        """
        analyzer = NetworkAnalyzer(config={}, network=network)
        centrality_methods = {
            'betweenness': analyzer.calc_betweenness_centrality,
            'degree': analyzer.calc_degree_centrality
        }
        return centrality_methods[centrality_measure]()
