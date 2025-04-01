import networkx as nx


class AttackStrategyExecuter:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

    def run(self):
        pass
