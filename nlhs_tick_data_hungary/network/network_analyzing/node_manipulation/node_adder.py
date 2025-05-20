from typing import Tuple

import networkx as nx
import numpy as np

from nlhs_tick_data_hungary.network.network_analyzing import MetricCalculator
from nlhs_tick_data_hungary.network.network_analyzing import NetworkAnalyzer


class NodeAdder:
    """
    Class responsible for adding new nodes to a network and connecting them to existing nodes. Furthermore, it
    measures the robustness of the network with different network metrics.
    """

    def __init__(self, network: nx.Graph, config: dict):
        """
        Initializes the NodeAdder with a network and configuration settings.

        :param network: The network to which nodes will be added.
        :param config: Dictionary containing configuration details (e.g. nodes_to_add, num_of_connections,
         defending_metric).
        """
        self.network = network
        self.config = config

        self.nodes_added = []  # Keeps track of the number/index of nodes added
        self.metric_results = []  # Stores metric values computed after each node addition
        self.sum_of_new_weights = 0
        self.sum_of_all_path_lengths = 0

    def run(self):
        """
        Runs the process of adding new nodes to the network to measure robustness.
        """
        # Determine the overall range of weights across existing links in the network
        weight_range = self.determine_weight_range()

        if self.config['defending_metric'] == 'APL' and not nx.is_connected(self.network):
            analyzer = NetworkAnalyzer(config={}, network=self.network)
            self.sum_of_all_path_lengths += analyzer.sum_path_lengths()
            print('Kiszámoltam az utakat')

        # Loop from 1 up to the configured number of nodes to add for the network
        for i in range(1, self.config['nodes_to_add'] + 1):
            # Add a new node to the network
            new_node_id = self.add_new_node()
            # Add a new node to the network
            self.connect_to_existing_nodes(new_node_id=new_node_id,
                                           weight_range=weight_range)

            # Calculate the current network metric after the new node has been added and connected
            metric_value = self.calc_metric_value()

            # Track the metric value for each added node
            self.nodes_added.append(i)
            self.metric_results.append(metric_value)

    def determine_weight_range(self) -> Tuple[int, int]:
        """
        Determines the minimum and maximum weights present on the network's links.
        This range is then used to generate random weights for the links that will connect the new node.

        :return Tuple[int, int]: A tuple representing the range of existing link weights.
        """
        # Extract all weights from the link data in the network
        weights = [data['weight'] for _, _, data in self.network.edges(data=True)]
        return min(weights), max(weights)

    def add_new_node(self) -> int:
        """
        Adds a new node to the network.
        The new node receives an id that is one greater than the maximum existing node id. If no nodes exist,
         the id starts at 0.

        :return int: The identifier of the newly added node.
        """
        # Calculate the new node id as one greater than the current maximum node id
        new_node_id = max(self.network.nodes, default=-1) + 1
        self.network.add_node(new_node_id)  # Add the new node to the network
        return new_node_id

    def connect_to_existing_nodes(self, new_node_id: int, weight_range: Tuple[int, int]):
        """
        Connects the newly added node to a subset of the existing nodes in the network.
        A maximum of 'num_of_connections' links are added, and for each link a random weight is generated within
         the specified `weight_range`.

        :param int new_node_id: The identifier of the newly added node.
        :param Tuple[int, int] weight_range: A tuple containing (min_weight, max_weight) to use for generating
         random link weights.
        """
        # Create a list of existing nodes (excluding the new node)
        existing_nodes = list(self.network.nodes() - {new_node_id})
        # Determine the number of nodes to connect to:
        # either the configured number or the size of existing nodes, whichever is smaller
        num_connections = min(self.config['num_of_connections'], len(existing_nodes))
        # Randomly choose the nodes to which the new node will be connected, without replacement
        nodes_to_connect_to = list(np.random.choice(existing_nodes, size=num_connections, replace=False))
        min_weight, max_weight = weight_range  # Unpack the weight range

        # Create a link from the new node to each selected existing node with a random weight assigned
        links = []
        for node in nodes_to_connect_to:
            new_weight = np.random.uniform(min_weight, max_weight)
            links.append((new_node_id, node, {'weight': new_weight}))
            self.sum_of_all_path_lengths += new_weight

        self.network.add_edges_from(links)  # Add the generated links to the network

    def calc_metric_value(self) -> float:
        """
        Calculates a metric for network defending that reflects the current state of the network.
        The metric to be calculated is determined by the 'defending_metric' value in the configuration parameters.

        :return float: The computed metric value from the MetricCalculator.
        """
        return MetricCalculator.calc_node_defending_metric(network=self.network,
                                                           metric=self.config['defending_metric'],
                                                           sum_of_path_lengths=self.sum_of_all_path_lengths)
