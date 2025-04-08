import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.node_remover import NodeRemover


class NodeAttacker:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.results = {
            'fraction_removed': [],
            'connectivity loss': []
        }

    def run(self):
        pass