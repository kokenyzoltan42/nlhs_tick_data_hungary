import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.metric_calculator import MetricCalculator


class NodeAdder:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.nodes_added = []  # Itt lehet elég egy for ciklus
        self.metric_results = []

    def run(self):
        pass

    def determine_weight_range(self):
        pass

    def add_new_node(self):
        pass

    def connect_to_existing_nodes(self):
        pass