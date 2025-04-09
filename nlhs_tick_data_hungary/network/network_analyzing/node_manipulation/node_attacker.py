import networkx as nx
import pandas as pd

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.node_remover import NodeRemover


class NodeAttacker:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.results = None

    def run(self):
        node_remover = NodeRemover(network=self.network, config=self.config)
        node_remover.run()

        self.results = pd.DataFrame(index=node_remover.fraction_of_nodes_removed,
                                    data=node_remover.connectivity_losses)
