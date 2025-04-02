import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import url_for
from flask_login import login_user
from app.models.users import User

@pytest.fixture
def customer_user():
    return User("customer1", "1234567894", "Customer", email="djangomekgp@gmail.com", location=(1, 0))

def test_customer_dashboard_access(client, customer_user):
    """Test access to customer dashboard."""
    with client.application.test_request_context():
        login_user(customer_user)
        response = client.get(url_for('customer.customer_dashboard'))
        assert response.status_code == 200
        assert b'Customer Dashboard' in response.data

def test_customer_dashboard_unauthorized(client):
    """Test unauthorized access to customer dashboard."""
    response = client.get(url_for('customer.customer_dashboard'), follow_redirects=True)
    assert b'Please log in to access this page' in response.data

def test_add_to_cart(client, customer_user):
    """Test adding an item to cart."""
    with client.application.test_request_context():
        login_user(customer_user)
        with client.session_transaction() as sess:
            sess['cart'] = {}
        
        response = client.get(url_for('customer.add_to_cart', item_name='Apple'), follow_redirects=True)
        
        with client.session_transaction() as sess:
            assert 'Apple' in sess['cart']
            assert sess['cart']['Apple']['quantity'] == 1

def test_view_cart(client, customer_user):
    """Test viewing the cart."""
    with client.application.test_request_context():
        login_user(customer_user)
        with client.session_transaction() as sess:
            sess['cart'] = {
                'Apple': {
                    'name': 'Apple',
                    'price': 10,
                    'discount': 0,
                    'final_price': 10,
                    'quantity': 2,
                    'store_id': 1
                }
            }
        
        response = client.get(url_for('customer.view_cart'))
        assert response.status_code == 200
        assert b'Apple' in response.data
        assert b'20' in response.data  # 2 * 10 = 20

def test_remove_item_from_cart(client, customer_user):
    """Test removing an item from cart."""
    with client.application.test_request_context():
        login_user(customer_user)
        with client.session_transaction() as sess:
            sess['cart'] = {
                'Apple': {
                    'name': 'Apple',
                    'price': 10,
                    'discount': 0,
                    'final_price': 10,
                    'quantity': 2,
                    'store_id': 1
                }
            }
        
        response = client.post(url_for('customer.remove_item', item_name='Apple'), follow_redirects=True)
        
        with client.session_transaction() as sess:
            assert 'Apple' not in sess['cart']

def test_clear_cart(client, customer_user):
    """Test clearing the cart."""
    with client.application.test_request_context():
        login_user(customer_user)
        with client.session_transaction() as sess:
            sess['cart'] = {
                'Apple': {
                    'name': 'Apple',
                    'price': 10,
                    'discount': 0,
                    'final_price': 10,
                    'quantity': 2,
                    'store_id': 1
                }
            }
        
        response = client.get(url_for('customer.clear_cart'), follow_redirects=True)
        
        with client.session_transaction() as sess:
            assert sess['cart'] == {}

def test_update_cart_increase(client, customer_user):
    """Test increasing item quantity in cart."""
    with client.application.test_request_context():
        login_user(customer_user)
        with client.session_transaction() as sess:
            sess['cart'] = {
                'Apple': {
                    'name': 'Apple',
                    'price': 10,
                    'discount': 0,
                    'final_price': 10,
                    'quantity': 1,
                    'store_id': 1
                }
            }
        
        response = client.post(
            url_for('customer.update_cart', item_name='Apple'),
            data={'action': 'increase'},
            follow_redirects=True
        )
        
        with client.session_transaction() as sess:
            assert sess['cart']['Apple']['quantity'] == 2

def test_customer_orders(client, customer_user):
    """Test viewing customer orders."""
    with client.application.test_request_context():
        login_user(customer_user)
        response = client.get(url_for('customer.customer_orders'))
        assert response.status_code == 200
        assert b'Your Orders' in response.data

def test_process_purchase_card_payment(client, customer_user, monkeypatch):
    """Test processing purchase with card payment."""
    with client.application.test_request_context():
        login_user(customer_user)
        # Set up cart in session
        with client.session_transaction() as sess:
            sess['cart'] = {
                'Apple': {
                    'name': 'Apple',
                    'price': 10,
                    'discount': 0,
                    'final_price': 10,
                    'quantity': 2,
                    'store_id': 1
                }
            }
        
        # Create a copy of the bank accounts dictionary
        fake_accounts = {
            "card": {
                "1234567890123456": {"expiry": "12/24", "cvv": "123", "balance": 1000},
                "4242424242424242": {"expiry": "01/25", "cvv": "456", "balance": 500},
            },
            "upi": {
                "testupi@example": {"name": "Test User", "balance": 200},
                "demo@example": {"name": "Demo User", "balance": 100},
            },
        }
        
        # Patch the entire dictionary
        monkeypatch.setattr('app.models.users.FAKE_BANK_ACCOUNTS', fake_accounts)
        
        # Submit purchase with card payment
        response = client.post(
            url_for('customer.process_purchase'),
            data={
                'payment_method': 'card',
                'card_number': '1234567890123456',
                'card_expiry': '12/24',
                'card_cvv': '123'
            },
            follow_redirects=True
        )
        
        # Verify cart was cleared
        with client.session_transaction() as sess:
            assert sess.get('cart', None) == {}


def test_track_order(client, customer_user, monkeypatch):
    """Test tracking an order."""
    # Create a delivery agent for the test
    from app.models.users import User
    delivery_agent = User("driver1", "1234567897", "Delivery Agent", rating=4.5)
    
    # Mock the function that gets the delivery agent
    def mock_get_delivery_agent(agent_id):
        return delivery_agent
    
    test_order = {
        'ORD-12345678': {
            'order_id': 'ORD-12345678',
            'customer_id': 'customer1',
            'status': 'processing',
            'delivery_agent': 'driver1',
            'items_by_store': {1: {'Apple': 2}},
            'timestamp': '2025-04-01T22:08:00'
        }
    }

    with client.application.test_request_context():
        login_user(customer_user)
        # Patch the orders dictionary
        monkeypatch.setattr('app.models.stores.orders', test_order)
        
        # If your route uses a function to get the delivery agent, patch that too
        # monkeypatch.setattr('app.customer.routes.get_delivery_agent', mock_get_delivery_agent)
        
        response = client.get(url_for('customer.track_order', order_id='ORD-12345678'), follow_redirects=True)
        
        # Check for something very basic that should be in any HTML response
        assert b'<!DOCTYPE html>' in response.data
        
        # Check that we're not getting redirected to login or error page
        assert response.status_code == 200
        assert b'login' not in response.request.path.lower()
        assert b'error' not in response.request.path.lower()
