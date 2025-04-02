import matplotlib.pyplot as plt
import networkx as nx

# Create delivery network graph
delivery_graph = nx.Graph()

# Add nodes to the graph
nodes = ["Admin Office", "Store A", "Store B", "Store C", "Customer 1", "Customer 2", "Customer 3"]
delivery_graph.add_nodes_from(nodes)

# Add edges with weights (distances in km)
edges = [
    ("Admin Office", "Store A", 5),
    ("Admin Office", "Store B", 6),
    ("Admin Office", "Store C", 7),
    ("Store A", "Customer 1", 4),
    ("Store A", "Customer 2", 3),
    ("Store B", "Customer 2", 2),
    ("Store B", "Customer 3", 5),
    ("Store C", "Customer 1", 6),
    ("Store C", "Customer 3", 4)
]
delivery_graph.add_weighted_edges_from(edges)

# Define custom positions for a more balanced layout
graph_positions = {
    "Admin Office": (0, 0),
    "Store A": (-1, 1),
    "Store B": (-1, -1),
    "Store C": (1, 1),
    "Customer 1": (1, 0),
    "Customer 2": (-2, 0),
    "Customer 3": (0, -1)
}

# Draw the graph
plt.figure(figsize=(8, 6))
nx.draw(
    delivery_graph,
    pos=graph_positions,
    with_labels=True,
    node_size=3000,
    node_color="lightblue",
    font_size=10,
    font_weight="bold",
    edge_color="gray"
)
plt.title("Delivery Network Graph")
plt.show()
