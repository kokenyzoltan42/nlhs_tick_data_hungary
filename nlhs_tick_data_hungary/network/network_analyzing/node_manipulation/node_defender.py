import networkx as nx
import pandas as pd

from nlhs_tick_data_hungary.network.network_analyzing import NodeAdder


class NodeDefender:
    """
    A class that enhances a network by adding nodes based on a given configuration.
    """

    def __init__(self, network: nx.Graph, config: dict):
        """
        Initializes the NodeDefender with a network and configuration settings.


        :param nx.Graph network: A Graph object (from networkx) containing the network to be analysed.
        :param dict config: Configuration settings for modifying the network.
        """
        self.network = network
        self.config = config

        self.results = None

    def run(self):
        """
        Executes the node addition process and stores results.

        This method creates an instance of `NodeAdder`, runs it to add nodes, and stores the computed metrics
        in a DataFrame.
        """
        node_adder = NodeAdder(network=self.network, config=self.config)
        node_adder.run()

        # Store the results in a DataFrame
        self.results = pd.DataFrame(index=node_adder.nodes_added,
                                    data=node_adder.metric_results)
