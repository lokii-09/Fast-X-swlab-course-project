import pytest
import networkx as nx
from unittest.mock import patch
from app.models.stores import orders
from app.models.users import users, delivery_graph, graph_positions
from app.utils.algo import assign_driver  # Adjust import path as needed

@pytest.fixture
def setup_test_data():
    """Setup test data for the delivery network"""
    # Clear existing data
    orders.clear()
    users.clear()
    delivery_graph.clear()
    
    # Set up test graph
    nodes = ["Admin Office", "Store A", "Store B", "Store C", "Customer 1", "Customer 2", "Customer 3"]
    delivery_graph.add_nodes_from(nodes)
    
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
    
    # Set up graph positions
    graph_positions.update({
        "Admin Office": (0, 0),
        "Store A": (-1, 1),
        "Store B": (-1, -1),
        "Store C": (1, 1),
        "Customer 1": (1, 0),
        "Customer 2": (-2, 0),
        "Customer 3": (0, -1)
    })
    
    # Add test users
    users.extend([
        {"username": "driver1", "user_type": "Delivery Agent", "location": (0, 0)},
        {"username": "driver2", "user_type": "Delivery Agent", "location": (-1, 1)},
        {"username": "customer1", "user_type": "Customer", "location": (1, 0)}
    ])
    
    yield
    
    # Clean up after tests
    orders.clear()
    users.clear()
    delivery_graph.clear()
    graph_positions.clear()

def test_assign_driver_basic(setup_test_data):
    """Test basic driver assignment with a simple order"""
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}},
        "customer_location": (1, 0)
    }
    
    driver, route = assign_driver(order)
    assert driver in ["driver1", "driver2"]
    assert route == [1]  # Only one store to visit

def test_assign_driver_multiple_stores_small(setup_test_data):
    """Test driver assignment with multiple stores (≤ 4)"""
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}, 2: {"Banana": 1}, 3: {"Orange": 3}},
        "customer_location": (1, 0)
    }
    
    driver, route = assign_driver(order)
    assert driver in ["driver1", "driver2"]
    assert len(route) == 3  # Should visit all 3 stores
    assert set(route) == {1, 2, 3}  # All stores should be in the route

def test_assign_driver_multiple_stores_large(setup_test_data, monkeypatch):
    """Test driver assignment with many stores (> 4)"""
    # Mock permutations to simulate many stores
    def mock_permutations(*args, **kwargs):
        raise MemoryError("Too many permutations")
    
    monkeypatch.setattr("itertools.permutations", mock_permutations)
    
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}, 2: {"Banana": 1}, 3: {"Orange": 3}},
        "customer_location": (1, 0)
    }
    
    driver, route = assign_driver(order)
    assert driver in ["driver1", "driver2"]
    assert len(route) == 3  # Should visit all 3 stores
    assert set(route) == {1, 2, 3}  # All stores should be in the route

def test_assign_driver_no_drivers(setup_test_data):
    """Test when no drivers are available"""
    users.clear()  # Remove all users
    
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}},
        "customer_location": (1, 0)
    }
    
    driver, route = assign_driver(order)
    assert driver is None
    assert route == []

def test_assign_driver_busy_drivers(setup_test_data):
    """Test with busy drivers who have existing orders"""
    # Add a busy driver with an existing order
    orders["ORD-EXISTING"] = {
        "delivery_agent": "driver1",
        "status": "preparing",
        "delivered": False,
        "customer_location": (-2, 0)  # Customer 2's location
    }
    
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}},
        "customer_location": (1, 0)
    }
    
    driver, route = assign_driver(order)
    # driver2 should be preferred as driver1 is busy
    assert driver == "driver2"

def test_assign_driver_all_busy(setup_test_data):
    """Test when all drivers are busy"""
    # Make all drivers busy
    orders["ORD-EXISTING1"] = {
        "delivery_agent": "driver1",
        "status": "preparing",
        "delivered": False,
        "customer_location": (-2, 0)  # Customer 2's location
    }
    
    orders["ORD-EXISTING2"] = {
        "delivery_agent": "driver2",
        "status": "preparing",
        "delivered": False,
        "customer_location": (0, -1)  # Customer 3's location
    }
    
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}},
        "customer_location": (1, 0)
    }
    
    driver, route = assign_driver(order)
    assert driver in ["driver1", "driver2"]  # Any driver can be chosen based on distance

def test_assign_driver_coordinate_mapping(setup_test_data):
    """Test driver location coordinate mapping"""
    # Add a driver with coordinates that don't directly map to a node
    users.append({
        "username": "driver3", 
        "user_type": "Delivery Agent", 
        "location": (100, 100)  # Coordinates that don't match any node
    })
    
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}},
        "customer_location": (1, 0)
    }
    
    driver, route = assign_driver(order)
    assert driver in ["driver1", "driver2", "driver3"]
    # driver3 should use the default "Admin Office" node

def test_network_error_handling(setup_test_data, monkeypatch):
    """Test handling of network errors"""
    def mock_shortest_path_length(*args, **kwargs):
        raise nx.NetworkXNoPath("No path found")
    
    monkeypatch.setattr(nx, "shortest_path_length", mock_shortest_path_length)
    
    order = {
        "customer_id": "customer1",
        "items_by_store": {1: {"Apple": 2}},
        "customer_location": (1, 0)
    }
    
    # Should handle the exception gracefully
    driver, route = assign_driver(order)
    assert driver is None
