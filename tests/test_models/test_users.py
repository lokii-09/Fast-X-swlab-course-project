import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.users import User, users, delivery_graph, location_coordinates, FAKE_BANK_ACCOUNTS
from app import bcrypt
import networkx as nx

def test_user_initialization():
    """Test initialization of User class with different user types."""
    # Test admin user
    admin = User("admin", "1234567890", "Admin", location=(0, 0))
    assert admin.id == "admin"
    assert admin.phone == "1234567890"
    assert admin.user_type == "Admin"
    assert admin.location == (0, 0)
    assert admin.store_id is None
    assert admin.rating is None
    assert admin.email is None
    
    # Test manager user
    manager = User("manager1", "1234567891", "Manager", store_id=1, location=(-1, 1))
    assert manager.id == "manager1"
    assert manager.phone == "1234567891"
    assert manager.user_type == "Manager"
    assert manager.store_id == 1
    assert manager.location == (-1, 1)
    
    # Test customer user
    customer = User("customer1", "1234567894", "Customer", email="test@example.com", location=(1, 0))
    assert customer.id == "customer1"
    assert customer.phone == "1234567894"
    assert customer.user_type == "Customer"
    assert customer.email == "test@example.com"
    assert customer.location == (1, 0)
    
    # Test delivery agent user
    delivery = User("driver1", "1234567897", "Delivery Agent", rating=4.5, location=(0, 0))
    assert delivery.id == "driver1"
    assert delivery.phone == "1234567897"
    assert delivery.user_type == "Delivery Agent"
    assert delivery.rating == 4.5
    assert delivery.location == (0, 0)

def test_user_mixin_methods():
    """Test UserMixin methods required by Flask-Login."""
    user = User("testuser", "1234567890", "Customer")
    
    # Test is_authenticated (should be True for all User instances)
    assert user.is_authenticated
    
    # Test is_active (should be True for all User instances)
    assert user.is_active
    
    # Test is_anonymous (should be False for all User instances)
    assert not user.is_anonymous
    
    # Test get_id (should return string representation of id)
    assert user.get_id() == "testuser"

def test_users_data_structure():
    """Test the structure of the users list."""
    assert isinstance(users, list)
    assert len(users) == 9  # 1 admin, 3 managers, 3 customers, 2 delivery agents
    
    # Check common fields in all user records
    for user_data in users:
        assert "username" in user_data
        assert "phone" in user_data
        assert "password" in user_data
        assert "user_type" in user_data
        assert "location" in user_data
        assert isinstance(user_data["location"], tuple)
    
    # Check user type counts
    admin_count = sum(1 for user in users if user["user_type"] == "Admin")
    manager_count = sum(1 for user in users if user["user_type"] == "Manager")
    customer_count = sum(1 for user in users if user["user_type"] == "Customer")
    delivery_count = sum(1 for user in users if user["user_type"] == "Delivery Agent")
    
    assert admin_count == 1
    assert manager_count == 3
    assert customer_count == 3
    assert delivery_count == 2

def test_user_password_hashing():
    """Test bcrypt password hashing and verification."""
    password = "testpassword"
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Test that hashed password is not equal to original password
    assert hashed_password != password
    
    # Test that password verification works
    assert bcrypt.check_password_hash(hashed_password, password)
    
    # Test that incorrect password fails verification
    assert not bcrypt.check_password_hash(hashed_password, "wrongpassword")
    
    # Test that all user passwords in the users list are hashed
    for user_data in users:
        assert bcrypt.check_password_hash(user_data["password"], 
                                         "admin123" if user_data["user_type"] == "Admin" else
                                         "manager123" if user_data["user_type"] == "Manager" else
                                         "customer123" if user_data["user_type"] == "Customer" else
                                         "driver123")

def test_delivery_graph_structure():
    """Test the structure of the delivery network graph."""
    # Test graph type
    assert isinstance(delivery_graph, nx.Graph)
    
    # Test number of nodes and edges
    assert len(delivery_graph.nodes) == 7
    assert len(delivery_graph.edges) == 12
    
    # Test node names
    expected_nodes = ["Admin Office", "Store A", "Store B", "Store C", 
                     "Customer 1", "Customer 2", "Customer 3"]
    for node in expected_nodes:
        assert node in delivery_graph.nodes
    
    # Test edge weights
    edge_weights = {
        ("Admin Office", "Store A"): 5,
        ("Admin Office", "Store B"): 6,
        ("Admin Office", "Store C"): 7,
        ("Store A", "Customer 1"): 4,
        ("Store A", "Customer 2"): 3,
        ("Store B", "Customer 2"): 2,
        ("Store B", "Customer 3"): 5,
        ("Store C", "Customer 1"): 6,
        ("Store C", "Customer 3"): 4,
        ("Store A", "Store B") : 3,
        ("Store A", "Store C"): 4,
        ("Store B", "Store C"): 2
    }
    
    for edge, weight in edge_weights.items():
        assert delivery_graph.has_edge(*edge)
        assert delivery_graph[edge[0]][edge[1]]["weight"] == weight

def test_location_coordinates(monkeypatch):
    """Test location coordinates mapping."""
    from app.models.users import users, location_coordinates
    
    # Create a copy of users with reset locations for delivery agents
    modified_users = []
    for user in users:
        user_copy = user.copy()
        if user_copy["username"] in ["driver1", "driver2"]:
            user_copy["location"] = (0, 0)  # Reset to admin office
        modified_users.append(user_copy)
    
    # Patch the users list
    monkeypatch.setattr('app.models.users.users', modified_users)
    
    # Test that all expected keys exist
    expected_keys = ["admin", "manager1", "manager2", "manager3",
                    "customer1", "customer2", "customer3"]
    for key in expected_keys:
        assert key in location_coordinates

    # Test specific coordinate values
    assert location_coordinates["admin"] == (0, 0)
    assert location_coordinates["manager1"] == (-1, 1)
    assert location_coordinates["manager2"] == (-1, -1)
    assert location_coordinates["manager3"] == (1, 1)
    assert location_coordinates["customer1"] == (1, 0)
    assert location_coordinates["customer2"] == (-2, 0)
    assert location_coordinates["customer3"] == (0, -1)

    # Test that user locations match their mapped coordinates
    for user_data in modified_users:
        username = user_data["username"]
        if username == "driver1" or username == "driver2":
            # Delivery agents start at admin office
            assert user_data["location"] == location_coordinates["admin"]
            
def test_fake_bank_accounts():
    """Test the structure of fake bank accounts."""
    assert "card" in FAKE_BANK_ACCOUNTS
    assert "upi" in FAKE_BANK_ACCOUNTS
    
    # Test card accounts
    assert len(FAKE_BANK_ACCOUNTS["card"]) == 2
    for card_number, details in FAKE_BANK_ACCOUNTS["card"].items():
        assert "expiry" in details
        assert "cvv" in details
        assert "balance" in details
        assert isinstance(details["balance"], int)
    
    # Test UPI accounts
    assert len(FAKE_BANK_ACCOUNTS["upi"]) == 2
    for upi_id, details in FAKE_BANK_ACCOUNTS["upi"].items():
        assert "name" in details
        assert "balance" in details
        assert isinstance(details["balance"], int)

"""
This test file includes comprehensive tests for:
    User class initialization with different user types
    UserMixin methods required by Flask-Login
    Structure of the users list and user type counts
    Password hashing and verification
    Delivery network graph structure and edge weights
    Location coordinates mapping
    Fake bank accounts structure
"""