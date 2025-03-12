import networkx as nx
import random

from nlhs_tick_data_hungary.network.network_analyzing.network_analyzer import NetworkAnalyzer


class NodeManipulation:
    # TODO: utánanéni, hogy pontosan hogyan máküdik a csúcs hozzáadás. Itt úgy oldottam meg, hogy random, és be lehet
    #  álítani, hogy hány csúcshoz kösse hozzá (legyen ez is random?). Cikkben csak annyi van írva, hogy
    #  véletlenszerűen köti hozzá a hálózathoz.

    # TODO: valami nem stimmel az LCC-vel (sima y=x lineáris egyenes az eredmény (valamit félreértettem biztosan))
    """
    A class that simulates node manipulation (addition for network defending and removal for network attacking)
    on a given network graph. The simulation behavior is determined by the provided configuration dictionary.

    Documentation: https://arxiv.org/pdf/2006.05648
    """

    def __init__(self, network: nx.Graph, config: dict):
        """
        Initializes the NodeManipulation instance.

        :param nx.Graph network: A networkx graph object.
        :param dict config: A dictionary specifying the simulation configuration. It must include a key 'mode'
                       with value either 'defending' (node addition) or 'attacking' (node removal).
        """
        self.original_graph = network
        # Work on a copy so that the original network remains unchanged. (It may or may not come in handy later)
        self.simulation_network = network.copy()
        self.config = config

    def run_simulation(self) -> dict:
        """
        Runs the simulation based on the configuration mode.

        :return dict: A dictionary with keys 'x' and 'y', where 'x' is a list of x-axis values and 'y' is a list
                 of measured network metric values.
        """
        mode = self.config['mode'].lower()  # Retrieve the mode (defending or attacking) from the config
        if mode == 'defending':
            return self.run_defending()  # Run defending scenario
        elif mode == 'attacking':
            return self.run_attacking()  # Run attacking scenario

    def run_defending(self) -> dict:
        """
        Simulates a network defending scenario by adding nodes to the network.

        Each iteration:
          - A new node is added with a label determined as one greater than the current maximum node (or 0 if empty).
          - The new node is connected to k randomly chosen existing nodes (k is specified in the config).
          - The network metric (APL or LCC) is computed using the NetworkAnalyzer.

        The results are stored for plotting:
          - x-axis: number of nodes added.
          - y-axis: corresponding measured metric value.

        :return dict: A dictionary with keys 'x' and 'y' for plotting.
        """
        iterations = self.config['iterations']  # Number of iterations for the defending simulation
        k = self.config['k']  # Number of nodes each new node should connect to
        metric = self.config['metric'].upper()  # Either "APL" or "LCC"
        results = {'x': [], 'y': []}  # Dictionary to store results for plotting

        # Run simulation for the specified number of iterations
        for i in range(1, iterations + 1):
            # Determine a new node label
            if self.simulation_network.nodes:
                new_node = max(self.simulation_network.nodes) + 1
            else:
                new_node = 0  # If no nodes exist, the first node will be labeled 0
            self.simulation_network.add_node(new_node)

            # Connect the new node to k existing nodes (if fewer than k exist, connect to all)
            existing_nodes = list(self.simulation_network.nodes)
            # Exclude the new node itself (in order to not become its own neighbor)
            existing_nodes.remove(new_node)
            if existing_nodes:
                if len(existing_nodes) <= k:
                    neighbors = existing_nodes
                else:
                    neighbors = random.sample(existing_nodes, k)  # Select random neighbors
                for neighbor in neighbors:
                    # Add edge with default weight 1
                    self.simulation_network.add_edge(new_node, neighbor, weight=1)

            # Compute the chosen metric using NetworkAnalyzer
            # TODO: ez legyen inkább tagváltozó? (úgy mőködik?)
            analyzer = NetworkAnalyzer(config={}, network=self.simulation_network)
            if metric == 'APL':
                metric_value = analyzer.calc_average_path_length()
            elif metric == 'LCC':
                metric_value = analyzer.calc_largest_connected_component()
            else:
                metric_value = None

            results['x'].append(i)  # Number of nodes added so far
            results['y'].append(metric_value)  # Store the metric value for plotting

        return results

    def run_attacking(self) -> dict:
        """
        Simulates a network attacking scenario by removing nodes from the network.

        The simulation supports different attack strategies defined by the 'attack_type' parameter in the config:
          - "random": remove nodes in random order.
          - "betweenness": compute betweenness centrality once, sort nodes descending, and remove in that order.
          - "degree": compute degree centrality once, sort nodes descending, and remove in that order.
          - "cascading_betweenness": at each iteration, compute betweenness centrality
           and remove the node with the highest value.
          - "cascading_degree": similar, but using degree centrality.

        In each iteration the following are recorded:
          - Fraction of nodes removed (x-axis).
          - Connectivity

        The simulation stops when 1 node remains.

        :return dict: A dictionary with keys 'x' and 'y' for plotting the attack impact.
        """
        attack_type = self.config['attack_type'].lower()  # Get the attack type from the config
        results = {'x': [], 'y': []}  # Dictionary to store results for plotting

        initial_num_nodes = self.simulation_network.number_of_nodes()  # Initial number of nodes in the network
        analyzer_initial = NetworkAnalyzer(config={}, network=self.simulation_network)
        initial_lcc = analyzer_initial.calc_largest_connected_component()  # Calculate initial LCC size

        removed_count = 0  # Counter for the number of nodes removed

        # For non-cascading strategies (betweenness, degree), determine the removal order once.
        removal_order = []
        if attack_type in ['betweenness', 'degree']:
            analyzer = NetworkAnalyzer(config={}, network=self.simulation_network)
            if attack_type == 'betweenness':
                centrality = analyzer.calc_betweenness_centrality()  # Calculate betweenness centrality
            else:  # degree centrality
                centrality = analyzer.calc_degree_centrality()  # Calculate degree centrality
            removal_order = sorted(centrality, key=centrality.get, reverse=True)  # Sort nodes by centrality

        # Continue removal until the network is reduced to 1 or 0 nodes.
        while self.simulation_network.number_of_nodes() > 1:
            if attack_type == 'random':
                node_to_remove = random.choice(list(self.simulation_network.nodes))  # Randomly select a node
            elif attack_type in ['betweenness', 'degree']:
                if removal_order:
                    node_to_remove = removal_order.pop(0)  # Remove the node with the highest centrality
                    if node_to_remove not in self.simulation_network:
                        continue
                else:
                    break
            elif attack_type == 'cascading_betweenness':
                centrality = nx.algorithms.centrality.betweenness_centrality(self.simulation_network, weight='weight')
                node_to_remove = max(centrality, key=centrality.get)  # Select the node with the highest betweenness
            elif attack_type == 'cascading_degree':
                centrality = nx.algorithms.centrality.degree_centrality(self.simulation_network)
                node_to_remove = max(centrality, key=centrality.get)  # Select the node with the highest degree
            else:
                raise ValueError("Not available attack type")

            self.simulation_network.remove_node(node_to_remove)  # Remove the node from the network
            removed_count += 1

            fraction_removed = removed_count / initial_num_nodes  # Calculate fraction of nodes removed

            analyzer_current = NetworkAnalyzer(config={}, network=self.simulation_network)
            current_lcc = analyzer_current.calc_largest_connected_component()  # Calculate current LCC size

            # Calculate connectivity loss as the difference in LCC sizes relative to the initial LCC size.
            connectivity_loss = (initial_lcc - current_lcc) / initial_lcc if initial_lcc > 0 else 0
            results['x'].append(fraction_removed)  # Store the fraction of nodes removed
            results['y'].append(connectivity_loss)  # Store the connectivity loss

        return results
