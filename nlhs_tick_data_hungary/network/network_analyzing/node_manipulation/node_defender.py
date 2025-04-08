import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.node_adder import NodeAdder


class NodeDefender:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.results = {'nodes_added': None,
                        'metric': None}

    def run(self):
        pass
