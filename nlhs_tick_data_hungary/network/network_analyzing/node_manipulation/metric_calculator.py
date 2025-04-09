import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing.network_analyzer import NetworkAnalyzer


class MetricCalculator:
    @staticmethod
    def calc_lcc(network: nx.Graph) -> int:
        analyzer = NetworkAnalyzer(config={}, network=network)
        return analyzer.calc_size_of_largest_connected_component()

    @staticmethod
    def calc_connectivity_loss(initial_lcc: int, current_lcc: int):
        return (initial_lcc - current_lcc) / initial_lcc

    @staticmethod
    def calc_node_defending_metric(network: nx.Graph, metric: str):
        analyzer = NetworkAnalyzer(config={}, network=network)
        metric_methods = {
            'APL': analyzer.calc_average_path_length(),
            'LCC': analyzer.calc_size_of_largest_connected_component()
        }
        return metric_methods[metric]

    @staticmethod
    def calc_centrality(network: nx.Graph, centrality_measure: str) -> dict:
        analyzer = NetworkAnalyzer(config={}, network=network)
        centrality_methods = {
            'betweenness': analyzer.calc_betweenness_centrality(),
            'degree': analyzer.calc_degree_centrality()
        }
        return centrality_methods[centrality_measure]
