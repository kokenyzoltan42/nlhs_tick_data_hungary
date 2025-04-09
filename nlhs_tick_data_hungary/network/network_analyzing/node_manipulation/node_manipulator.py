import networkx as nx

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.node_attacker import NodeAttacker
from nlhs_tick_data_hungary.network.network_analyzing.node_manipulation.node_defender import NodeDefender


class NodeManipulator:
    """
    A class to manipulate nodes in a network graph to analyze robustness and vulnerability.
    Supports two simulation modes: defending (adding nodes) and attacking (removing nodes).
    """
    # TODO: Update docstrings if necessary (probably)
    def __init__(self, network: nx.Graph, config: dict):
        """
        Initializes the NodeManipulator with a network and configuration settings.

        Configuration settings (meaning of the keys in the dictionary):
        - 'manipulation_type': Run this kind of simulation, e.g.: 'defending', 'attacking'
        - 'num_of_connections': The number of connections to establish at each node addition (only used
        during 'defending' simulations)
        - `nodes_to_add`: Number of nodes to add (only used during 'defending' simulations)
        - 'metric': What metric to use, e.g.: 'APL', 'LCC' (only used during 'defending' simulations)
        - 'attack_type': Type node removal strategy, e.g.: initial_betweenness, cascading_betweenness,
         random (only used during 'attacking' simulations)


        (A more thorough description of this class is available at the Wiki page)

        :param nx.Graph network: The input network graph.
        :param dict config: A dictionary containing simulation parameters.
        """
        self.network = network
        self.config = config

    def run_simulation(self) -> dict:
        """
        Runs the simulation based on the selected mode.

        :return dict: A dictionary with simulation results.
        """
        simulation_modes = {
            'defending': NodeAttacker(network=self.network, config=self.config),
            'attacking': NodeDefender(network=self.network, config=self.config)
        }
        chosen_simulation = simulation_modes[self.config['manipulation_type']]
        chosen_simulation.run()

        return chosen_simulation.results
