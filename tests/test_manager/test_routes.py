import pytest
from flask import url_for
from flask_login import login_user
from app.models.users import User
from app.models.stores import stores, orders
from app import create_app

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = 'localhost'
    return app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def manager_user():
    return User("manager1", "1234567891", "Manager")

@pytest.fixture
def customer_user():
    return User("customer1", "1234567894", "Customer")

def test_manager_dashboard_access(client, manager_user):
    with client.application.test_request_context():
        login_user(manager_user)
        response = client.get(url_for('manager.manager_dashboard'))
        assert response.status_code == 200
        assert b'Manager Dashboard' in response.data

def test_manager_dashboard_unauthorized(client, customer_user):
    with client.application.test_request_context():
        login_user(customer_user)
        response = client.get(url_for('manager.manager_dashboard'), follow_redirects=True)
        assert b'You do not have permission to access this page' in response.data

def test_manager_orders_access(client, manager_user):
    with client.application.test_request_context():
        login_user(manager_user)
        response = client.get(url_for('manager.manager_orders'))
        assert response.status_code == 200
        assert b'Store Orders' in response.data

def test_manager_orders_unauthorized(client, customer_user):
    with client.application.test_request_context():
        login_user(customer_user)
        response = client.get(url_for('manager.manager_orders'), follow_redirects=True)
        assert b'Access denied' in response.data

def test_add_item_access(client, manager_user):
    with client.application.test_request_context():
        login_user(manager_user)
        response = client.get(url_for('manager.add_item'))
        assert response.status_code == 200
        assert b'Add New Item' in response.data

def test_add_item_unauthorized(client, customer_user):
    with client.application.test_request_context():
        login_user(customer_user)
        response = client.get(url_for('manager.add_item'), follow_redirects=True)
        assert b'You do not have permission to access this page' in response.data

def test_add_item_success(client, manager_user):
    with client.application.test_request_context():
        login_user(manager_user)
        # First get the form to extract the CSRF token
        response = client.get(url_for('manager.add_item'))
        html = response.data.decode()
        
        # Extract CSRF token (you might need to use regex or a parser like BeautifulSoup)
        import re
        csrf_token = re.search('name="csrf_token" value="(.+?)"', html).group(1)
        
        # Now submit the form with the CSRF token
        data = {
            'item_name': 'Test Item',
            'item_type': 'Test Type',
            'price': 10.0,
            'stock': 100,
            'discount': 0,
            'csrf_token': csrf_token,
            'submit': 'Add Item'  # Include the submit button value
        }
        response = client.post(url_for('manager.add_item'), data=data, follow_redirects=True)
        assert response.status_code == 200
        assert 'Test Item' in stores[1]['items']


def test_add_existing_item(client, manager_user):
    with client.application.test_request_context():
        login_user(manager_user)
        stores[1]['items']['Existing Item'] = {
            'price': 5.0,
            'stock': 50,
            'discount': 0,
            'item_type': 'Existing Type'
        }
        data = {
            'item_name': 'Existing Item',
            'item_type': 'Test Type',
            'price': 10.0,
            'stock': 100,
            'discount': 0
        }
        response = client.post(url_for('manager.add_item'), data=data, follow_redirects=True)
        print(response.data.decode())  # Print the response HTML for debugging
        assert response.status_code == 200

"""
This test file covers:

1. Testing access to the manager dashboard for authenticated managers
2. Testing unauthorized access to the manager dashboard
3. Testing access to the manager orders page for authenticated managers
4. Testing unauthorized access to the manager orders page
5. Testing access to the add item page for authenticated managers
6. Testing unauthorized access to the add item page
7. Testing successful addition of a new item
8. Testing attempt to add an existing item
"""
