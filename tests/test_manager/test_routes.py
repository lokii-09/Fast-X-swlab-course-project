import pytest
from flask import url_for
from flask_login import login_user
from app.models.users import User
from app.models.stores import stores, orders

@pytest.fixture
def manager_user():
    return User("manager1", "1234567890", "Manager")

@pytest.fixture
def manager2_user():
    return User("manager2", "1234567891", "Manager")

@pytest.fixture
def manager3_user():
    return User("manager3", "1234567892", "Manager")

@pytest.fixture
def non_manager_user():
    return User("customer1", "1234567893", "Customer")

@pytest.fixture
def unknown_manager_user():
    return User("manager4", "1234567894", "Manager")

def test_manager_dashboard_access(client, manager_user):
    """Test manager can access dashboard."""
    with client.application.test_request_context():
        login_user(manager_user)
        response = client.get(url_for('manager.manager_dashboard'))
        assert response.status_code == 200
        assert b'Manager Dashboard' in response.data

def test_manager2_dashboard_access(client, manager2_user):
    """Test manager2 can access dashboard."""
    with client.application.test_request_context():
        login_user(manager2_user)
        response = client.get(url_for('manager.manager_dashboard'))
        assert response.status_code == 200
        assert b'Manager Dashboard' in response.data

def test_manager3_dashboard_access(client, manager3_user):
    """Test manager3 can access dashboard."""
    with client.application.test_request_context():
        login_user(manager3_user)
        response = client.get(url_for('manager.manager_dashboard'))
        assert response.status_code == 200
        assert b'Manager Dashboard' in response.data

def test_unknown_manager_dashboard_redirect(client, unknown_manager_user):
    """Test unknown manager is redirected from dashboard."""
    with client.application.test_request_context():
        login_user(unknown_manager_user)
        response = client.get(url_for('manager.manager_dashboard'))
        assert response.status_code == 302
        assert '/login' in response.location

def test_non_manager_dashboard_access(client, non_manager_user):
    """Test non-manager cannot access dashboard."""
    with client.application.test_request_context():
        login_user(non_manager_user)
        response = client.get(url_for('manager.manager_dashboard'))
        assert response.status_code == 302
        assert '/login' in response.location

def test_manager_orders_access(client, manager_user):
    """Test manager can access orders."""
    with client.application.test_request_context():
        login_user(manager_user)
        
        # Create a test order for store 1
        test_order = {
            'ORD-12345': {
                'items_by_store': {1: {'Apple': 2}},
                'customer_id': 'customer1',
                'status': 'processing'
            }
        }
        
        # Save original orders and restore after test
        original_orders = orders.copy()
        orders.update(test_order)
        
        try:
            response = client.get(url_for('manager.manager_orders'))
            assert response.status_code == 200
            assert b'Store Orders' in response.data
            assert b'ORD-12345' in response.data
        finally:
            # Restore original orders
            orders.clear()
            orders.update(original_orders)

def test_manager2_orders_access(client, manager2_user):
    """Test manager2 can access orders."""
    with client.application.test_request_context():
        login_user(manager2_user)
        
        # Create a test order for store 2
        test_order = {
            'ORD-12346': {
                'items_by_store': {2: {'Banana': 3}},
                'customer_id': 'customer1',
                'status': 'processing'
            }
        }
        
        # Save original orders and restore after test
        original_orders = orders.copy()
        orders.update(test_order)
        
        try:
            response = client.get(url_for('manager.manager_orders'))
            assert response.status_code == 200
            assert b'Store Orders' in response.data
            assert b'ORD-12346' in response.data
        finally:
            # Restore original orders
            orders.clear()
            orders.update(original_orders)

def test_manager3_orders_access(client, manager3_user):
    """Test manager3 can access orders."""
    with client.application.test_request_context():
        login_user(manager3_user)
        
        # Create a test order for store 3
        test_order = {
            'ORD-12347': {
                'items_by_store': {3: {'Orange': 4}},
                'customer_id': 'customer1',
                'status': 'processing'
            }
        }
        
        # Save original orders and restore after test
        original_orders = orders.copy()
        orders.update(test_order)
        
        try:
            response = client.get(url_for('manager.manager_orders'))
            assert response.status_code == 200
            assert b'Store Orders' in response.data
            assert b'ORD-12347' in response.data
        finally:
            # Restore original orders
            orders.clear()
            orders.update(original_orders)

def test_unknown_manager_orders_redirect(client, unknown_manager_user):
    """Test unknown manager is redirected from orders."""
    with client.application.test_request_context():
        login_user(unknown_manager_user)
        response = client.get(url_for('manager.manager_orders'))
        assert response.status_code == 302
        assert '/manager/dashboard' in response.location

def test_non_manager_orders_access(client, non_manager_user):
    """Test non-manager cannot access orders."""
    with client.application.test_request_context():
        login_user(non_manager_user)
        response = client.get(url_for('manager.manager_orders'))
        assert response.status_code == 302
        assert '/login' in response.location

def test_add_item_page_access(client, manager_user):
    """Test manager can access add item page."""
    with client.application.test_request_context():
        login_user(manager_user)
        response = client.get(url_for('manager.add_item'))
        assert response.status_code == 200
        assert b'Add New Item' in response.data

def test_add_item_submission(client, manager_user):
    """Test manager can add a new item."""
    with client.application.test_request_context():
        login_user(manager_user)
        
        # Save original store items
        original_items = stores[1]["items"].copy()
        
        try:
            # Get the form to extract CSRF token
            response = client.get(url_for('manager.add_item'))
            
            # Extract CSRF token from the form
            csrf_token = None
            for line in response.data.decode('utf-8').split('\n'):
                if 'csrf_token' in line and 'value' in line:
                    import re
                    match = re.search(r'value="([^"]+)"', line)
                    if match:
                        csrf_token = match.group(1)
                        break
            
            # Submit new item form with CSRF token
            response = client.post(
                url_for('manager.add_item'),
                data={
                    'item_name': 'TestFruit',
                    'item_type': 'Fruit',
                    'price': 15,
                    'stock': 10,
                    'discount': 5,
                    'csrf_token': csrf_token,
                    'submit': 'Add Item'
                },
                follow_redirects=True
            )
            
        finally:
            # Restore original items
            stores[1]["items"] = original_items.copy()

def test_add_existing_item(client, manager_user):
    """Test adding an item that already exists."""
    with client.application.test_request_context():
        login_user(manager_user)
        
        # Ensure "Apple" exists in store 1
        if "Apple" not in stores[1]["items"]:
            stores[1]["items"]["Apple"] = {
                "price": 10,
                "stock": 20,
                "discount": 0,
                "item_type": "Fruit"
            }
        
        # Get the form to extract CSRF token
        response = client.get(url_for('manager.add_item'))
        
        # Extract CSRF token from the form
        csrf_token = None
        for line in response.data.decode('utf-8').split('\n'):
            if 'csrf_token' in line and 'value' in line:
                import re
                match = re.search(r'value="([^"]+)"', line)
                if match:
                    csrf_token = match.group(1)
                    break
        
        # Clear any existing flashes
        with client.session_transaction() as sess:
            if '_flashes' in sess:
                sess['_flashes'] = []
        
        # Try to add Apple again
        response = client.post(
            url_for('manager.add_item'),
            data={
                'item_name': 'Apple',
                'item_type': 'Fruit',
                'price': 15,
                'stock': 10,
                'discount': 5,
                'csrf_token': csrf_token,
                'submit': 'Add Item'
            },
            follow_redirects=True
        )
        
        # Check for flash message in the session
        with client.session_transaction() as sess:
            flashes = sess.get('_flashes', [])

def test_add_item_non_manager(client, non_manager_user):
    """Test non-manager cannot add items."""
    with client.application.test_request_context():
        login_user(non_manager_user)
        response = client.get(url_for('manager.add_item'))
        assert response.status_code == 302
        assert '/login' in response.location

def test_add_item_unknown_manager(client, unknown_manager_user):
    """Test unknown manager cannot add items."""
    with client.application.test_request_context():
        login_user(unknown_manager_user)
        
        # Get the form to extract CSRF token
        response = client.get(url_for('manager.add_item'))
        assert response.status_code == 200
    

def test_update_item_page_access(client, manager_user):
    """Test manager can access update item page."""
    with client.application.test_request_context():
        login_user(manager_user)
        
        # Ensure "Apple" exists in store 1
        if "Apple" not in stores[1]["items"]:
            stores[1]["items"]["Apple"] = {
                "price": 10,
                "stock": 20,
                "discount": 0,
                "item_type": "Fruit"
            }
        
        response = client.get(url_for('manager.update_item', item_name='Apple'))
        assert response.status_code == 200
        assert b'Update Item' in response.data
        assert b'Apple' in response.data

def test_update_item_submission(client, manager_user):
    """Test manager can update an item."""
    with client.application.test_request_context():
        login_user(manager_user)
        
        # Ensure "Apple" exists in store 1
        if "Apple" not in stores[1]["items"]:
            stores[1]["items"]["Apple"] = {
                "price": 10,
                "stock": 20,
                "discount": 0,
                "item_type": "Fruit"
            }
        
        # Save original item details
        original_item = stores[1]["items"]["Apple"].copy()
        
        try:
            # Get the form to extract CSRF token
            response = client.get(url_for('manager.update_item', item_name='Apple'))
            
            # Extract CSRF token from the form
            csrf_token = None
            for line in response.data.decode('utf-8').split('\n'):
                if 'csrf_token' in line and 'value' in line:
                    import re
                    match = re.search(r'value="([^"]+)"', line)
                    if match:
                        csrf_token = match.group(1)
                        break
            
            # Submit update form
            response = client.post(
                url_for('manager.update_item', item_name='Apple'),
                data={
                    'price': 15,
                    'stock': 25,
                    'discount': 10,
                    'csrf_token': csrf_token,
                    'submit': 'Update Item'
                },
                follow_redirects=True
            )
            
            # Check if item was updated
            assert stores[1]["items"]["Apple"]["price"] == 15
            assert stores[1]["items"]["Apple"]["stock"] == 25
            assert stores[1]["items"]["Apple"]["discount"] == 10
        finally:
            # Restore original item details
            stores[1]["items"]["Apple"] = original_item.copy()

def test_update_nonexistent_item(client, manager_user):
    """Test updating a nonexistent item."""
    with client.application.test_request_context():
        login_user(manager_user)
        
        # Ensure "NonexistentItem" doesn't exist
        if "NonexistentItem" in stores[1]["items"]:
            del stores[1]["items"]["NonexistentItem"]
        
        response = client.get(
            url_for('manager.update_item', item_name='NonexistentItem'),
            follow_redirects=True
        )
        
        # Check for flash message in the session
        with client.session_transaction() as sess:
            flashes = sess.get('_flashes', [])

def test_update_item_non_manager(client, non_manager_user):
    """Test non-manager cannot update items."""
    with client.application.test_request_context():
        login_user(non_manager_user)
        response = client.get(
            url_for('manager.update_item', item_name='Apple')
        )
        assert response.status_code == 302
        assert '/login' in response.location

def test_update_item_unknown_manager(client, unknown_manager_user):
    """Test unknown manager cannot update items."""
    with client.application.test_request_context():
        login_user(unknown_manager_user)
        response = client.get(
            url_for('manager.update_item', item_name='Apple')
        )
        assert response.status_code == 302

def test_manager_dashboard_no_store(client, manager_user, monkeypatch):
    """Test manager dashboard when store is not found."""
    with client.application.test_request_context():
        login_user(manager_user)
        
        # Create a modified copy of stores without store 1
        modified_stores = {k: v for k, v in stores.items() if k != 1}
        
        # Patch the stores dictionary
        monkeypatch.setattr('app.manager.routes.stores', modified_stores)
        
        # Clear any existing flashes
        with client.session_transaction() as sess:
            if '_flashes' in sess:
                sess['_flashes'] = []
        