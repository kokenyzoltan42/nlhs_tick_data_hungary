import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing.network_analyzer import NetworkAnalyzer


class NodeAttacker:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.results = {
            'fraction_removed': [],
            'connectivity loss': []
        }

    def run(self):
        initil_num_of_nodes = self.network.number_of_nodes()
        initial_lcc = self.compute_lcc()
        num_of_removed_nodes = 0

        removal_order = self.get_removal_order()

        while self.network.number_of_nodes() > 1:
            node_to_remove = self.select_nodes_to_remove(removal_order=removal_order)
            num_of_removed_nodes += 1
            fraction_removed = num_of_removed_nodes / initil_num_of_nodes
            current_lcc = self.compute_lcc()
            connectivity_loss = (initial_lcc - current_lcc) / initial_lcc if initial_lcc > 0 else 0
            self.results['fraction_removed'].append(fraction_removed)
            self.results['connectivity loss'].append(connectivity_loss)

    def compute_lcc(self) -> int:
        """
        Computes the size of the largest connected component (LCC) in the network.

        :return int: Size of the largest connected component.
        """
        analyzer = NetworkAnalyzer(config={}, network=self.network)
        return analyzer.calc_size_of_largest_connected_component()

    def get_removal_order(self) -> list:
        pass

    def select_nodes_to_remove(self, removal_order: list):
        # Itt lesz példányosítva a strategies
        pass
