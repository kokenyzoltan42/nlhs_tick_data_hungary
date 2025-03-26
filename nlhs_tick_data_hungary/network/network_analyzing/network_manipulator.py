import random

import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing.network_analyzer import NetworkAnalyzer


class NodeManipulator:
    """
    A class to manipulate nodes in a network graph to analyze robustness and vulnerability.
    Supports two simulation modes: defending (adding nodes) and attacking (removing nodes).
    """

    def __init__(self, network: nx.Graph, config: dict):
        """
        Initializes the NodeManipulator with a network and configuration settings.

        :param nx.Graph network: The input network graph.
        :param dict config: Dictionary containing simulation parameters.
        """
        self.original_graph = network
        self.simulation_network = network.copy()
        self.config = config
        self.weight_range = self._determine_weight_range()

        # The results are stored in this way in order to easily plot the results. The values in 'x' key will appear
        # on the horizontal axis and the values in the 'y' key will appear on the vertical axis
        self.results = {
            'x': [],
            'y': []
        }

    def run_simulation(self) -> dict:
        """
        Runs the simulation based on the selected mode.

        :return dict: A dictionary with simulation results.
        """
        simulation_modes = {
            'defending': self.run_defending,
            'attacking': self.run_attacking
        }
        simulation_modes.get(self.config['mode'], lambda: None)()

        return self.results

    def run_defending(self) -> None:
        """
        Executes the defending mode by iteratively adding new nodes to the network. The results are stored in the
        `results` member variable.
        """
        for i in range(1, self.config['iterations'] + 1):
            new_node = self._add_new_node()
            self._connect_to_existing_nodes(new_node, self.config['k'])
            metric_value = self._compute_metric()
            self.results['x'].append(i)
            self.results['y'].append(metric_value)

    def run_attacking(self) -> None:
        """
        Executes the attacking mode by progressively removing nodes from the network.
        At every node removal this method also measures the connectivity loss, which is calculated as follows:
        (initial_lcc - current_lcc) / initial_lcc
        """
        initial_num_nodes = self.simulation_network.number_of_nodes()
        initial_lcc = self._compute_lcc()
        removed_count = 0

        removal_order = self._get_removal_order()

        while self.simulation_network.number_of_nodes() > 1:
            node_to_remove = self._select_node_to_remove(removal_order)
            if node_to_remove is None:
                break

            self.simulation_network.remove_node(node_to_remove)
            removed_count += 1
            fraction_removed = removed_count / initial_num_nodes
            current_lcc = self._compute_lcc()
            # Measuring connectivity
            connectivity_loss = (initial_lcc - current_lcc) / initial_lcc if initial_lcc > 0 else 0
            self.results['x'].append(fraction_removed)
            self.results['y'].append(connectivity_loss)

    def _determine_weight_range(self) -> tuple:
        """
        Determines the range of edge weights in the network.

        :return tuple: A tuple containing minimum and maximum of the edges' weights.
        """
        weights = [data['weight'] for _, _, data in self.simulation_network.edges(data=True)]
        return min(weights), max(weights)

    def _add_new_node(self) -> int:
        """
        Adds a new node to the network with an incremented node ID.

        :return int: The newly added node ID.
        """
        new_node = max(  # We use max instead, because it's not guaranteed that the nodes' ids are continuous
            self.simulation_network.nodes,
            default=-1  # In case of the network is empty the newly added node's id should be 0.
        ) + 1
        self.simulation_network.add_node(new_node)
        return new_node

    def _connect_to_existing_nodes(self, new_node: int, k: int):
        """
        Connects the newly added node to `k` existing nodes with random weights.

        :param int new_node: The newly added node ID.
        :param int k: Number of connections to establish.
        """
        existing_nodes = list(self.simulation_network.nodes - {new_node})
        neighbors = random.sample(existing_nodes, min(k, len(existing_nodes)))

        min_weight, max_weight = self.weight_range

        edges = [
            (new_node, neighbor, {'weight': random.uniform(min_weight, max_weight)})
            for neighbor in neighbors
        ]

        self.simulation_network.add_edges_from(edges)

    def _compute_metric(self) -> float:
        """
        Computes a given network metric.
        Currently implemented metrics: 'APL' and 'LCC'.

        :return float: Computed metric value.
        """
        analyzer = NetworkAnalyzer(config={}, network=self.simulation_network)
        metric_methods = {
            'APL': analyzer.calc_average_path_length,
            'LCC': analyzer.calc_largest_connected_component
        }
        return metric_methods.get(self.config['metric'], lambda: None)()

    def _compute_lcc(self) -> int:
        """
        Computes the size of the largest connected component (LCC) in the network.

        :return int: Size of the largest connected component.
        """
        analyzer = NetworkAnalyzer(config={}, network=self.simulation_network)
        return analyzer.calc_size_of_largest_connected_component()

    def _get_removal_order(self) -> list:
        """
        Determines the order of node removal based on centrality measures.

        :return list: Ordered list of nodes to remove.
        """
        if self.config['attack_type'] in ['betweenness', 'degree']:
            analyzer = NetworkAnalyzer(config={}, network=self.simulation_network)
            centrality_methods = {
                'betweenness': analyzer.calc_betweenness_centrality,
                'degree': analyzer.calc_degree_centrality
            }
            centrality = centrality_methods.get(self.config['attack_type'], lambda: {})()
            return sorted(centrality, key=centrality.get, reverse=True)
        return []

    def _select_node_to_remove(self, removal_order: list) -> int | None:
        """
        Selects a node for removal based on the attack strategy.

        :param list removal_order: Precomputed list of nodes to remove.
        :return dict: The node ID to remove.
        """
        if self.config['attack_type'] in ['betweenness', 'degree']:
            while removal_order:
                node = removal_order.pop(0)
                if node in self.simulation_network:
                    return node
            return None  # If every node has been removed

        attack_methods = {
            'random': lambda: random.choice(list(self.simulation_network.nodes)),
            'cascading_betweenness': lambda: max(nx.betweenness_centrality(self.simulation_network, weight='weight'),
                                                 key=nx.betweenness_centrality(self.simulation_network,
                                                                               weight='weight').get),
            'cascading_degree': lambda: max(nx.degree_centrality(self.simulation_network),
                                            key=nx.degree_centrality(self.simulation_network).get)
        }
        return attack_methods.get(self.config['attack_type'], lambda: None)()
