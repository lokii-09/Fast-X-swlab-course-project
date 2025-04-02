from flask_login import UserMixin
import networkx as nx
from app import bcrypt

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
    ("Store C", "Customer 3", 4),
    ("Store A", "Store B", 3),
    ("Store A", "Store C", 4),
    ("Store B", "Store C", 2)
]
delivery_graph.add_weighted_edges_from(edges)


# Define custom positions for a more balanced layout (This is random, as we are not using euclidean distance for)
graph_positions = {
    "Admin Office": (0, 0),
    "Store A": (-1, 1),
    "Store B": (-1, -1),
    "Store C": (1, 1),
    "Customer 1": (1, 0),
    "Customer 2": (-2, 0),
    "Customer 3": (0, -1)
}

# Map locations to coordinates
location_coordinates = {
    "admin": (0, 0),  # Admin Office
    "manager1": (-1, 1),  # Store A
    "manager2": (-1, -1),  # Store B
    "manager3": (1, 1),  # Store C
    "customer1": (1, 0),  # Customer 1
    "customer2": (-2, 0),  # Customer 2
    "customer3": (0, -1),  # Customer 3
}

# Updated Hardcoded user data with graph-aligned locations
users = [
    {"username": "admin", "phone": "1234567890", "password": bcrypt.generate_password_hash("admin123").decode('utf-8'), "user_type": "Admin", "location": location_coordinates["admin"]},
    {"username": "manager1", "phone": "1234567891", "password": bcrypt.generate_password_hash("manager123").decode('utf-8'), "user_type": "Manager", "store_id": 1, "location": location_coordinates["manager1"]},
    {"username": "manager2", "phone": "1234567892", "password": bcrypt.generate_password_hash("manager123").decode('utf-8'), "user_type": "Manager", "store_id": 2, "location": location_coordinates["manager2"]},
    {"username": "manager3", "phone": "1234567893", "password": bcrypt.generate_password_hash("manager123").decode('utf-8'), "user_type": "Manager", "store_id": 3, "location": location_coordinates["manager3"]},
    {"username": "customer1", "phone": "1234567894", "password": bcrypt.generate_password_hash("customer123").decode('utf-8'), "user_type": "Customer", "location": location_coordinates["customer1"], "email": "djangomekgp@gmail.com"},
    {"username": "customer2", "phone": "1234567895", "password": bcrypt.generate_password_hash("customer123").decode('utf-8'), "user_type": "Customer", "location": location_coordinates["customer2"], "email": "djangomekgp@gmail.com"},
    {"username": "customer3", "phone": "1234567896", "password": bcrypt.generate_password_hash("customer123").decode('utf-8'), "user_type": "Customer", "location": location_coordinates["customer3"], "email": "djangomekgp@gmail.com"},
    {"username": "driver1", "phone": "1234567897", "password": bcrypt.generate_password_hash("driver123").decode('utf-8'), "user_type": "Delivery Agent", "rating": 4.5, "location": location_coordinates["admin"]},  # Start at Admin Office
    {"username": "driver2", "phone": "1234567898", "password": bcrypt.generate_password_hash("driver123").decode('utf-8'), "user_type": "Delivery Agent", "rating": 3.8, "location": location_coordinates["admin"]}  # Start at Admin Office
]

# Fake bank details for demonstration purposes
FAKE_BANK_ACCOUNTS = {
    "card": {
        "1234567890123456": {"expiry": "12/24", "cvv": "123", "balance": 1000},
        "4242424242424242": {"expiry": "01/25", "cvv": "456", "balance": 500},
    },
    "upi": {
        "testupi@example": {"name": "Test User", "balance": 200},
        "demo@example": {"name": "Demo User", "balance": 100},
    },
}

class User(UserMixin):
    def __init__(self, username, phone, user_type, store_id=None, rating=None, email=None, location=None):
        self.id = username
        self.email = email
        self.phone = phone
        self.user_type = user_type
        self.store_id = store_id
        self.rating = rating
        self.location = location
