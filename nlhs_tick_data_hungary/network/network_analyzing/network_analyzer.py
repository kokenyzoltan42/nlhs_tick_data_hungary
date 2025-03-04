import networkx as nx


class NetworkAnalyzer:
    def __init__(self, config: dict, network: nx.Graph):
        self.config = config
        self.network = network

        self.result: (dict | None) = None

    def run(self):
        for func_name, enabled in self.config.items():
            if enabled and hasattr(self, func_name):
                method = getattr(self, func_name)
                if callable(method):
                    result_key = func_name.replace("calc_", "")
                    self.result[result_key] = method()

    def calc_network_diameter(self) -> int:
        return nx.diameter(self.network, weight='weight')

    def calc_modularity(self):
        return nx.algorithms.community.quality.modularity(
            G=self.network,
            communities=nx.algorithms.community.label_propagation_communities(self.network)
        )

# TODO: `calc_average_degree_connectivity` eltávolítása az implementációs diagram leírásából
#  és talán a hub_taxa-t is

    def calc_number_of_communities(self) -> int:
        return len(nx.algorithms.community.label_propagation_communities(self.network))

    def calc_number_of_triangles(self) -> int:
        return nx.algorithms.cluster.triangles(G=self.network)

    def calc_largest_connected_component(self) -> set:
        # Bármennyire is írja, hogy Sized, ez `set`
        # TODO: leellenőrizni
        return max(nx.connected_components(G=self.network), key=len)

    def calc_average_path_length(self) -> float:
        # default method (ha van weight): ‘dijkstra’.
        return nx.algorithms.shortest_paths.generic.average_shortest_path_length(G=self.network, weight='weight')

    def calc_degree_centrality(self) -> dict:
        return nx.algorithms.centrality.degree_centrality(G=self.network)

    def calc_betweenness_centrality(self) -> dict:
        return nx.algorithms.centrality.betweenness_centrality(G=self.network,
                                                               weight='weight')

    def calc_closeness_centrality(self) -> dict:
        return nx.algorithms.centrality.closeness_centrality(G=self.network)

    def calc_eigenvector_centrality(self) -> dict:
        return nx.algorithms.centrality.eigenvector_centrality(G=self.network,
                                                               weight='weight')

    def calc_hub_taxa(self):
        pass
