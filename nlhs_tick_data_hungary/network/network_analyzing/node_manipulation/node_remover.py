import networkx as nx
import numpy as np

from nlhs_tick_data_hungary.network.network_analyzing import MetricCalculator


class NodeRemover:
    """
    Class responsible for removing nodes from a network based on different attack strategies. It tracks the fraction
    of nodes removed and the corresponding connectivity loss values.
    """

    def __init__(self, network: nx.Graph, config: dict):
        """
        Initializes the NodeRemover with a network and configuration settings.

        :param nx.Graph network: The network from which nodes will be removed.
        :param dict config: Dictionary containing attack type and other configuration details.
        """
        self.network = network
        self.config = config

        self.fraction_of_nodes_removed = []  # Stores the fraction of nodes removed
        self.connectivity_loss_values = []  # Stores connectivity loss values

    def run(self):
        """
        Executes the node removal process according to the specified attack strategy. Tracks how the removal of nodes
        affect the network's connectivity.
        """
        # Store initial node count
        initial_num_of_nodes = self.network.number_of_nodes()
        # Compute the size of the initial largest connected component
        initial_lcc = MetricCalculator.calc_lcc(network=self.network)
        removed_count = 0

        # Get the precomputed node removal order (if applicable)
        removal_order = self.get_removal_order()

        while self.network.number_of_nodes() > 1:
            # Select the next node to remove
            node_to_remove = self.select_node_to_remove(ordered_list=removal_order)
            if node_to_remove is None:
                break  # Stop if no valid node remains

            # Remove the selected node
            self.network.remove_node(node_to_remove)
            removed_count += 1
            # Compute the size of the largest connected component after a node has been removed
            current_lcc = MetricCalculator.calc_lcc(network=self.network)
            # Compute connectivity loss
            connectivity_loss = MetricCalculator.calc_connectivity_loss(initial_lcc=initial_lcc,
                                                                        current_lcc=current_lcc)

            # Track fraction removed
            self.fraction_of_nodes_removed.append(removed_count / initial_num_of_nodes)
            # Store connectivity loss
            self.connectivity_loss_values.append(connectivity_loss)

    def get_removal_order(self) -> list:
        """
        Determines the order in which nodes should be removed based on the initial centrality measures.

        :return list: A sorted list of nodes based on their centrality values (descending order) or an empty list.
        """
        if self.config['attack_type'] in ['initial_betweenness', 'initial_degree']:
            centrality_values = MetricCalculator.calc_centrality(
                network=self.network,
                centrality_measure=self.config['attack_type'].replace('initial_', '')
            )
            # Return nodes sorted by highest centrality first
            return sorted(centrality_values, key=centrality_values.get, reverse=True)

        return []  # Return empty list if no ordering is needed

    def select_node_to_remove(self, ordered_list: list) -> int:
        """
        Selects the next node to be removed based on the specified attack strategy. Delegates selection to specific
        methods based on the attack type.

        :param list ordered_list: List of nodes sorted by centrality if applicable.
        :return int: The id of the node to remove or None if no valid node is found.
        """
        if self.config['attack_type'] in ['initial_betweenness', 'initial_degree']:
            return self._select_from_initial_order(ordered_list=ordered_list)  # Use predefined order if applicable
        else:
            return self._select_cascading_or_random()  # Use alternative selection strategies

    def _select_from_initial_order(self, ordered_list: list) -> int | None:
        """
        Selects the next node to remove based on the precomputed removal order.

        :param list ordered_list: List of nodes sorted by centrality.
        :return int | None: The next node to remove or None if no valid node remains.
        """
        while ordered_list:
            selected_node = ordered_list.pop(0)  # Take the highest-priority node from the list
            if selected_node in self.network:
                return selected_node  # Return the node if it is still present in the network
        return None  # Return None if no valid node remains

    def _select_cascading_or_random(self) -> int:
        """
        Selects a node to remove based on cascading failure or random strategies. Uses centrality metrics (degree and
        betweenness) to determine the most critical node.

        :return int: The node to remove based on the given strategy.
        """

        if self.config['attack_type'] == 'random':
            return np.random.choice(list(self.network.nodes))

        elif self.config['attack_type'].startswith('cascading_'):
            centrality_metric = self.config['attack_type'].replace('cascading_', '')
            centrality = MetricCalculator.calc_centrality(network=self.network, centrality_measure=centrality_metric)
            return max(centrality, key=centrality.get)

        else:
            raise ValueError(f"No strategy implemented as {self.config['attack_type']}")
