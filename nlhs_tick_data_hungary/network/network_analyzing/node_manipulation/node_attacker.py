import networkx as nx


class NodeAttacker:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

    def run(self):
        pass

    def compute_lcc(self):
        pass

    def get_removal_order(self):
        pass

    def select_nodes_to_remove(self):
        # Itt lesz példányosítva a strategies
        pass
