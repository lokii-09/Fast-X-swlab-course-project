import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.stores import stores, orders, generate_order_id

def test_stores_structure():
    """Test that the stores dictionary has the correct structure."""
    assert isinstance(stores, dict)
    assert len(stores) == 3
    assert 1 in stores
    assert 2 in stores
    assert 3 in stores

def test_store_properties():
    """Test that each store has the required properties."""
    for store_id, store in stores.items():
        assert "name" in store
        assert "location" in store
        assert "manager" in store
        assert "items" in store
        assert isinstance(store["location"], tuple)
        assert isinstance(store["items"], dict)

def test_store_names():
    """Test that stores have the correct names."""
    assert stores[1]["name"] == "Store A"
    assert stores[2]["name"] == "Store B"
    assert stores[3]["name"] == "Store C"

def test_store_locations():
    """Test that stores have the correct locations."""
    assert stores[1]["location"] == (0, 0)
    assert stores[2]["location"] == (2, 3)
    assert stores[3]["location"] == (4, 2)

def test_store_managers():
    """Test that stores have the correct managers."""
    assert stores[1]["manager"] == "manager1"
    assert stores[2]["manager"] == "manager2"
    assert stores[3]["manager"] == "manager3"

def test_item_properties():
    """Test that items have the required properties."""
    for store_id, store in stores.items():
        for item_name, item in store["items"].items():
            assert "price" in item
            assert "stock" in item
            assert "discount" in item
            assert "item_type" in item
            assert isinstance(item["price"], int)
            assert isinstance(item["stock"], int)
            assert isinstance(item["discount"], int)
            assert isinstance(item["item_type"], str)

def test_common_items():
    """Test that some items are common across stores."""
    # Apple is in all stores
    assert "Apple" in stores[1]["items"]
    assert "Apple" in stores[2]["items"]
    assert "Apple" in stores[3]["items"]
    
    # Milk is in all stores
    assert "Milk" in stores[1]["items"]
    assert "Milk" in stores[2]["items"]
    assert "Milk" in stores[3]["items"]

def test_unique_items():
    """Test that some items are unique to specific stores."""
    # Rice is only in Store A
    assert "Rice" in stores[1]["items"]
    assert "Rice" not in stores[2]["items"]
    assert "Rice" not in stores[3]["items"]
    
    # Cereal is only in Store B
    assert "Cereal" not in stores[1]["items"]
    assert "Cereal" in stores[2]["items"]
    assert "Cereal" not in stores[3]["items"]
    
    # Cheese is only in Store C
    assert "Cheese" not in stores[1]["items"]
    assert "Cheese" not in stores[2]["items"]
    assert "Cheese" in stores[3]["items"]

def test_orders_empty_initially():
    """Test that orders dictionary is empty initially."""
    assert isinstance(orders, dict)
    assert len(orders) == 0

def test_generate_order_id():
    """Test that generate_order_id returns a string with the correct format."""
    order_id = generate_order_id()
    assert isinstance(order_id, str)
    assert order_id.startswith("ORD-")
    assert len(order_id) == 12  # "ORD-" + 8 characters
    
    # Generate multiple order IDs and check they're unique
    order_ids = [generate_order_id() for _ in range(10)]
    assert len(set(order_ids)) == 10  # All IDs should be unique


"""
Basic structure tests for the stores dictionary
    Tests for store properties (name, location, manager, items)
    Tests for item properties (price, stock, discount, item_type)
    Tests for common and unique items across stores
    Tests for the orders dictionary
    Tests for the generate_order_id function
"""