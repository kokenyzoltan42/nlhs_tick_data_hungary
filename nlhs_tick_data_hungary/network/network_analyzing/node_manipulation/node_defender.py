import networkx as nx
import pandas as pd

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.node_adder import NodeAdder


class NodeDefender:
    def __init__(self, network: nx.Graph, config: dict):
        self.network = network
        self.config = config

        self.results = None

    def run(self):
        node_adder = NodeAdder(network=self.network, config=self.config)
        node_adder.run()

        self.results = pd.DataFrame(index=node_adder.nodes_added,
                                    data=node_adder.metric_results)
