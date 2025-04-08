import networkx as nx


class MetricCalculator:
    @staticmethod
    def calc_lcc(network: nx.Graph) -> float:
        pass

    @staticmethod
    def calc_connectivity_loss(initial_lcc, current_lcc):
        pass

    @staticmethod
    def calc_node_defending_metric(network: nx.Graph, metric: str):
        pass

    @staticmethod
    def calc_centrality(network: nx.Graph, centrality_measure: str):
        pass
