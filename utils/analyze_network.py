# analyze_network.py

import networkx as nx
import matplotlib.pyplot as plt
import argparse
import numpy as np

import community as community_louvain

def load_network(file_path):
    """
    Load the network from a GEXF file.
    """
    try:
        G = nx.read_gexf(file_path)
        print(f"Loaded network from {file_path}.")
    except Exception as e:
        print(f"Error loading network: {e}")
        raise e
    return G

def basic_stats(G):
    """
    Print basic network statistics.
    """
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    degrees = [d for n, d in G.degree()]
    avg_degree = sum(degrees) / float(len(degrees)) if degrees else 0
    density = nx.density(G)
    avg_clustering = nx.average_clustering(G)
    
    print("----- Basic Network Statistics -----")
    print(f"Number of nodes: {num_nodes}")
    print(f"Number of edges: {num_edges}")
    print(f"Average degree: {avg_degree:.2f}")
    print(f"Density: {density:.4f}")
    print(f"Average clustering coefficient: {avg_clustering:.4f}")

    if nx.is_connected(G):
        avg_shortest_path = nx.average_shortest_path_length(G)
        print(f"Average shortest path length: {avg_shortest_path:.2f}")
    else:
        # Compute average shortest path for the largest connected component
        largest_cc = max(nx.connected_components(G), key=len)
        subgraph = G.subgraph(largest_cc)
        avg_shortest_path = nx.average_shortest_path_length(subgraph)
        print("Graph is not fully connected.")
        print(f"Average shortest path length (largest component): {avg_shortest_path:.2f}")
    print("------------------------------------\n")

def plot_degree_distribution(G):
    """
    Plot the degree distribution of the network.
    """
    degrees = [d for n, d in G.degree()]
    plt.figure(figsize=(8, 6))
    plt.hist(degrees, bins=range(1, max(degrees)+2), edgecolor="black", align="left")
    plt.title("Degree Distribution")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()

def detect_communities(G):
    """
    Detect communities in the network using the Louvain method.
    Returns a dictionary mapping node to community.
    """
    print("Performing community detection using the Louvain method...")
    partition = community_louvain.best_partition(G)
    num_communities = len(set(partition.values()))
    print(f"Detected {num_communities} communities.")
    return partition

def visualize_network(G, partition=None):
    """
    Visualize the network. If a partition (community structure) is provided,
    color nodes according to their community assignment.
    """
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, seed=42)  # fixed layout for reproducibility
    
    if partition:
        # Determine colors based on community assignment
        communities = set(partition.values())
        num_communities = len(communities)
        cmap = plt.get_cmap("viridis", num_communities)
        node_colors = [cmap(partition[node]) for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_size=50, node_color=node_colors, cmap=cmap)
    else:
        nx.draw_networkx_nodes(G, pos, node_size=50)
    
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    plt.title("Diplomatic Network Visualization")
    plt.axis("off")
    plt.show()

def main(file_path):
    # Load the network
    G = load_network(file_path)
    
    # Print basic statistics
    basic_stats(G)
    
    # Plot degree distribution
    plot_degree_distribution(G)
    
    # Detect communities and visualize network
    partition = detect_communities(G)
    visualize_network(G, partition)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze the diplomatic network from a GEXF file."
    )
    parser.add_argument(
        "file", 
        type=str, 
        help="Path to the GEXF file containing the network."
    )
    args = parser.parse_args()
    main(args.file)
