import networkx as nx
import random

import matplotlib
import matplotlib.pyplot as plt

from nlhs_tick_data_hungary.network.network_analyzing.node_manipulator import NodeManipulator

matplotlib.use('Qt5Agg')  # or another backend available in your environment


def create_connected_weighted_graph():
    network = nx.connected_watts_strogatz_graph(100, 30, 0.1, seed=69)
    # network = nx.barabasi_albert_graph(n=40, m=12)
    for (u, v) in network.edges():
        network[u][v]['weight'] = random.uniform(0.1, 10)
    return network


def run_defending_simulation(network):
    config_defending = {
        'mode': 'defending',
        'iterations': 50,
        'k': 4,
        'metric': 'APL'  # Valamiért LCC-nél csak egy lineáris egyenest ad vissza
    }
    nm_defend = NodeManipulator(network, config_defending)
    return nm_defend.run_simulation()


def run_attacking_simulation(network):
    config_attacking = {
        'mode': 'attacking',
        'attack_type': 'cascading_degree'
        # Can be 'random', 'betweenness', 'degree', 'cascading_betweenness', or 'cascading_degree'
    }
    nm_attack = NodeManipulator(network=network, config=config_attacking)
    return nm_attack.run_simulation()


def main():
    network = create_connected_weighted_graph()

    results_defend = run_defending_simulation(network)

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(results_defend['x'], results_defend['y'], marker='o', linestyle='-', color='blue')
    plt.xlabel('Number of nodes added')
    plt.ylabel('APL')
    plt.title('Defending')

    network_attack = create_connected_weighted_graph()
    results_attack = run_attacking_simulation(network_attack)

    plt.subplot(1, 2, 2)
    plt.plot(results_attack['x'], results_attack['y'], marker='o', linestyle='-', color='red')
    plt.xlabel('Fraction of nodes removed')
    plt.ylabel('Connectivity Loss')
    plt.title('Attacking')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
