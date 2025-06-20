import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from app.models.stores import stores
from app.models.users import users
from flask_login import login_user
from flask import session

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF protection for testing
    })
    
    # Create application context
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

# Test data fixture
@pytest.fixture
def test_stores():
    """Return a copy of the stores data for testing."""
    return stores.copy()

@pytest.fixture
def test_users():
    """Return a copy of the users data for testing."""
    return users.copy()

# Authentication fixtures
@pytest.fixture
def auth_client(client):
    """A test client with methods for authentication."""
    class AuthClient:
        def __init__(self, client):
            self.client = client
            
        def login(self, phone, password, user_type):
            return self.client.post('/login', data={
                'phone': phone,
                'password': password,
                'user_type': user_type
            }, follow_redirects=True)
            
        def logout(self):
            return self.client.get('/logout', follow_redirects=True)
    
    return AuthClient(client)

# User role-specific fixtures
@pytest.fixture
def admin_client(client, app):
    """A test client logged in as admin."""
    with client.session_transaction() as sess:
        sess['_user_id'] = 'admin'
    
    with app.test_request_context():
        from app.models.users import User
        admin_user = User('admin', '1234567890', 'Admin')
        login_user(admin_user)
        
    return client

@pytest.fixture
def manager_client(client, app):
    """A test client logged in as manager."""
    with client.session_transaction() as sess:
        sess['_user_id'] = 'manager1'
    
    with app.test_request_context():
        from app.models.users import User
        manager_user = User('manager1', '1234567891', 'Manager', store_id=1)
        login_user(manager_user)
        
    return client

@pytest.fixture
def customer_client(client, app):
    """A test client logged in as customer."""
    with client.session_transaction() as sess:
        sess['_user_id'] = 'customer1'
    
    with app.test_request_context():
        from app.models.users import User
        customer_user = User('customer1', '1234567894', 'Customer', 
                            email='djangomekgp@gmail.com', 
                            location=(1, 0))
        login_user(customer_user)
        
    return client

@pytest.fixture
def delivery_client(client, app):
    """A test client logged in as delivery agent."""
    with client.session_transaction() as sess:
        sess['_user_id'] = 'driver1'
    
    with app.test_request_context():
        from app.models.users import User
        delivery_user = User('driver1', '1234567897', 'Delivery Agent', 
                           rating=4.5, location=(0, 0))
        login_user(delivery_user)
        
    return  client

"""
This conftest.py file provides:
    An app fixture that creates a Flask application in testing mode
    A client fixture for making test requests
    A runner fixture for testing CLI commands
    Data fixtures (test_stores and test_users) to provide test data
    An auth_client fixture with login/logout helpers
    Role-specific client fixtures for admin, manager, customer and delivery agent
"""