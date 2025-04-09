import networkx as nx
import pandas as pd

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.node_remover import NodeRemover


class NodeAttacker:
    """
    A class that simulates an attack on a network by removing nodes based on a given configuration. Furthermore, it
    analyzes the network at each node removal.
    """

    def __init__(self, network: nx.Graph, config: dict):
        """
        Initializes the NodeAttacker with a network and configuration settings.

        :param nx.Graph network: A Graph object (from networkx) containing the network to be analysed.
        :param dict config: Configuration settings for modifying the network.
        """
        self.network = network
        self.config = config

        self.results = None

    def run(self):
        """
        Executes the node removal process and stores results.

        This method creates an instance of NodeRemover, runs it to remove nodes, and stores the computed
        connectivity loss values in a DataFrame.
        """
        node_remover = NodeRemover(network=self.network, config=self.config)
        node_remover.run()

        # Store the results in a DataFrame
        self.results = pd.DataFrame(index=node_remover.fraction_of_nodes_removed,
                                    data=node_remover.connectivity_loss_values)
