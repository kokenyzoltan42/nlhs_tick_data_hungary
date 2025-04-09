from typing import Tuple

import networkx as nx
import numpy as np

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.metric_calculator import MetricCalculator


class NodeAdder:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.nodes_added = []  # Itt lehet elég egy for ciklus
        self.metric_results = []

    def run(self):
        weight_range = self.determine_weight_range()

        for i in range(1, self.config['nodes_to_add'] + 1):
            new_node_id = self.add_new_node()
            self.connect_to_existing_nodes(new_node_id=new_node_id, weight_range=weight_range)
            metric_value = self.calc_metric_value()

            self.nodes_added.append(i)
            self.metric_results.append(metric_value)

    def determine_weight_range(self) -> Tuple[int, int]:
        weights = [data['weight'] for _, _, data in self.network.edges(data=True)]
        return min(weights), max(weights)

    def add_new_node(self):
        new_node_id = max(
            self.network.nodes,
            default=-1
        ) + 1

        self.network.add_node(new_node_id)

        return new_node_id

    def connect_to_existing_nodes(self, new_node_id: int, weight_range: Tuple[int, int]):
        existing_nodes = list(self.network.nodes() - {new_node_id})
        nodes_to_connect_to = np.random.choice(existing_nodes,
                                               size=min(self.config['num_of_connections'], len(existing_nodes)),
                                               replace=False)
        min_weight, max_weight = weight_range
        edges = [
            (new_node_id, nodes_to_connect_to, {'weight': np.random.uniform(low=min_weight, high=max_weight)})
        ]

        self.network.add_edges_from(edges)


    def calc_metric_value(self):
        return MetricCalculator.calc_node_defending_metric(network=self.network,
                                                           metric=self.config['defending_metric'])
