import networkx as nx
import numpy as np

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.metric_calculator import MetricCalculator


class NodeRemover:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.fraction_of_nodes_removed = []
        self.connectivity_losses = []

    def run(self):
        initial_num_of_nodes = self.network.number_of_nodes()
        initial_lcc = MetricCalculator.calc_lcc(network=self.network)
        removed_count = 0

        removal_order = self.get_removal_order()

        while self.network.number_of_nodes() > 1:
            node_to_remove = self.select_node_to_remove(order=removal_order)
            if node_to_remove is None:  # Ez biztos kell?
                break
            self.network.remove_node(node_to_remove)
            removed_count += 1
            self.fraction_of_nodes_removed.append(removed_count / initial_num_of_nodes)
            current_lcc = MetricCalculator.calc_lcc(network=self.network)

            connectivity_loss = MetricCalculator.calc_connectivity_loss(initial_lcc=initial_lcc,
                                                                        current_lcc=current_lcc)
            self.connectivity_losses.append(connectivity_loss)

    def get_removal_order(self):
        if self.config['attack_type'] in ['initial_betweenness', 'initial_degree']:
            # Calculate the centrality values for each node
            centrality_values = MetricCalculator.calc_centrality(
                network=self.network,
                centrality_measure=self.config['attack_type'].replace('initial_', '')
            )
            # Sort the values in descending order
            return sorted(centrality_values, reverse=True)

        # If the attack type doesn't require removal order, return an empty list
        return []

    def select_node_to_remove(self, order: list):  # elvileg list
        # TODO: ezt a metódust kettébontani, vagy legalábbis szebbé varázsolni
        if self.config['attack_type'] in ['initial_betweenness', 'initial_degree']:
            # Iterate through the removal order
            while order:
                # Select the next largest value in the list and drop it
                selected_node = order.pop(0)
                # If the selected node hasn't been already removed
                if selected_node in self.network:
                    return selected_node
        else:
            centrality_metric = str(self.config['attack_type'].replace('cascading_', ''))

            attack_methods = {
                'random': np.random.choice(list(self.network.nodes)),
                'cascading_betweenness': max(MetricCalculator.calc_centrality(network=self.network,
                                                                              centrality_measure=centrality_metric)),
                'cascading_degree': max(MetricCalculator.calc_centrality(network=self.network,
                                                                         centrality_measure=centrality_metric))
            }
            return attack_methods[self.config['attack_type']]
