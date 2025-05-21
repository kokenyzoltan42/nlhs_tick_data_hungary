from typing import Sized

import networkx as nx


class NetworkAnalyzer:
    """
    A class for analyzing various properties of a given network. The code assumes that the network is weighted and
    only contains positive weights.
    """

    def __init__(self, config: dict, network: nx.Graph):
        """
        Initializes the NetworkAnalyzer with a configuration dictionary and a network.

        :param dict config: Dictionary specifying which analysis methods to run.
        :param nx.Graph network: A NetworkX graph object.
        """
        self.config = config
        self.network = network
        self.result: (dict | None) = None

    def run(self):
        """
        This method runs the enabled analysis methods specified in the config dictionary.
        Stores results in the `result` attribute.
        """
        for func_name, enabled in self.config.items():
            if enabled and hasattr(self, func_name):
                method = getattr(self, func_name)
                if callable(method):
                    result_key = func_name.replace("calc_", "")
                    self.result[result_key] = method()

    def calc_network_diameter(self) -> int | None:
        """
        Calculates the diameter of the network, considering edge weights. If the network is not connected it returns
        the diameter of the largest connected component.
        :return int: The diameter of the network.
        """
        if nx.is_connected(self.network):
            return nx.diameter(self.network, weight='weight')
        else:
            largest_connected_component = self.calc_largest_connected_component()
            return nx.diameter(largest_connected_component, weight='weight')

    def calc_modularity(self) -> float:
        """
        Computes the modularity of the network based on community detection.
        :return float: The modularity of the network
        """
        return nx.algorithms.community.quality.modularity(
            G=self.network,
            communities=nx.algorithms.community.label_propagation_communities(self.network)
        )

    def calc_number_of_communities(self) -> int:
        """
        Determines the number of communities in the network.
        :return int: The number of detected communities.
        """
        return len(nx.algorithms.community.label_propagation_communities(self.network))

    def calc_number_of_triangles(self) -> int:
        """
        Calculates the number of triangles in the network. The built-in function counts the number of triangles that
        a node is in for every node. Since each triangle is counted as a triangle for each of the three nodes.
        Thus, the sum of the values should be 3 times the number of triangles.
        :return int: The total count of triangles in the network.
        """
        return int(sum(nx.algorithms.cluster.triangles(G=self.network).values()) / 3)

    def calc_largest_connected_component(self) -> Sized:
        """
        Finds the largest connected component of the network.
        :return Sized: The largest connected component as a set of nodes.
        """
        return self.network.subgraph(
            sorted(nx.connected_components(G=self.network), key=len, reverse=True)[0]
        )

    def calc_size_of_largest_connected_component(self) -> int:
        """
        Measuring the fraction of nodes contained in the largest connected component.
        (Larger value means more robust network)
        :return int: Size of the largest connected component
        """
        return len(self.calc_largest_connected_component())

    def calc_average_path_length(self) -> float:
        """
        Compute the average shortest path length in the network. If the network is not connected it calculates the
        convex combination of the average path lengths in every component

        :return float: The average shortest path length.
        """
        # If the network is connected, use the built-in function
        if nx.is_connected(G=self.network):
            return nx.average_shortest_path_length(
                G=self.network,
                weight='weight',
            )

        num_nodes = self.network.number_of_nodes()
        convex_combination = 0

        for subgraph in (self.network.subgraph(c).copy() for c in nx.connected_components(self.network)):
            apl_in_subgraph = nx.average_shortest_path_length(G=subgraph,
                                                              weight='weight')
            convex_coefficient = subgraph.number_of_nodes() / num_nodes
            convex_combination += convex_coefficient * apl_in_subgraph

        # Normalize by the total number of ordered node pairs
        return convex_combination

    def calc_degree_centrality(self) -> dict:
        """
        Calculates degree centrality for each node in the network.
        :return dict: A dictionary with nodes as keys and their degree centrality as values.
        """
        return nx.algorithms.centrality.degree_centrality(G=self.network)

    def calc_betweenness_centrality(self) -> dict:
        """
        Computes betweenness centrality for all nodes, considering edge weights.
        :return dict: A dictionary with nodes as keys and their betweenness centrality as values.
        """
        return nx.algorithms.centrality.betweenness_centrality(G=self.network, weight='weight')

    def calc_closeness_centrality(self) -> dict:
        """
        Calculates closeness centrality for each node.
        :return dict: A dictionary with nodes as keys and their closeness centrality as values.
        """
        return nx.algorithms.centrality.closeness_centrality(G=self.network)

    def calc_eigenvector_centrality(self) -> dict:
        """
        Computes eigenvector centrality, considering edge weights.
        :return dict: A dictionary with nodes as keys and their eigenvector centrality as values.
        """
        return nx.algorithms.centrality.eigenvector_centrality(G=self.network, weight='weight', max_iter=1000)

    def calc_average_weighted_degree(self) -> float:
        """
        Calculates the average weighted degree of the network.
        :return float: The average weighted degree.
        """
        total_weighted_degree = sum(dict(self.network.degree(weight='weight')).values())
        num_nodes = self.network.number_of_nodes()
        return total_weighted_degree / num_nodes if num_nodes > 0 else 0

    def calc_average_degree(self) -> float:
        """
        Computes the average degree of the network. This method only runs if the network is not a complete network.

        :return float: The average degree (not considering weights).
        """
        num_nodes = self.network.number_of_nodes()
        num_edges = self.network.number_of_edges()
        max_possible_edges = num_nodes * (num_nodes - 1) / 2  # Maximum edges in an undirected simple network

        # Check if the network is complete
        if num_edges < max_possible_edges:
            total_degree = sum(dict(self.network.degree()).values())
            return total_degree / num_nodes
        else:
            return 0
