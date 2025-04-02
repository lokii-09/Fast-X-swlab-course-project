import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import url_for
from flask_login import current_user
from app.models.users import User

def test_index_route(client):
    """Test the index route."""
    response = client.get(url_for('main.index'))
    assert response.status_code == 200
    assert b'Welcome to FastX' in response.data

def test_login_route_get(client):
    """Test the login route with GET method."""
    response = client.get(url_for('main.login'))
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Phone Number' in response.data
    assert b'Password' in response.data
    assert b'User Type' in response.data

def test_login_route_post_admin(auth_client):
    """Test admin login."""
    response = auth_client.login('1234567890', 'admin123', 'Admin')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_login_route_post_manager(auth_client):
    """Test manager login."""
    response = auth_client.login('1234567891', 'manager123', 'Manager')
    assert response.status_code == 200
    assert b'Manager Dashboard' in response.data

def test_login_route_post_customer(auth_client):
    """Test customer login."""
    response = auth_client.login('1234567894', 'customer123', 'Customer')
    assert response.status_code == 200
    assert b'Customer Dashboard' in response.data

def test_login_route_post_delivery(auth_client):
    """Test delivery agent login."""
    response = auth_client.login('1234567897', 'driver123', 'Delivery Agent')
    assert response.status_code == 200
    assert b'Delivery Dashboard' in response.data

def test_login_route_post_invalid_password(auth_client):
    """Test login with invalid password."""
    response = auth_client.login('1234567890', 'wrongpassword', 'Admin')
    assert response.status_code == 200
    assert b'Login Unsuccessful' in response.data

def test_login_route_post_invalid_phone(auth_client):
    """Test login with invalid phone number."""
    response = auth_client.login('9999999999', 'admin123', 'Admin')
    assert response.status_code == 200
    assert b'Login Unsuccessful' in response.data

def test_login_route_post_mismatched_user_type(auth_client):
    """Test login with mismatched user type."""
    response = auth_client.login('1234567890', 'admin123', 'Manager')
    assert response.status_code == 200
    assert b'Login Unsuccessful' in response.data

def test_logout_route(auth_client, client):
    """Test the logout route."""
    # First login
    auth_client.login('1234567890', 'admin123', 'Admin')
    
    # Then logout
    response = client.get(url_for('main.logout'), follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    assert b'Login' in response.data

def test_already_logged_in_redirect_admin(auth_client, client):
    """Test redirect when admin is already logged in."""
    auth_client.login('1234567890', 'admin123', 'Admin')
    response = client.get(url_for('main.login'), follow_redirects=True)
    assert b'Admin Dashboard' in response.data

def test_already_logged_in_redirect_manager(auth_client, client):
    """Test redirect when manager is already logged in."""
    auth_client.login('1234567891', 'manager123', 'Manager')
    response = client.get(url_for('main.login'), follow_redirects=True)
    assert b'Manager Dashboard' in response.data

def test_already_logged_in_redirect_customer(auth_client, client):
    """Test redirect when customer is already logged in."""
    auth_client.login('1234567894', 'customer123', 'Customer')
    response = client.get(url_for('main.login'), follow_redirects=True)
    assert b'Customer Dashboard' in response.data

def test_already_logged_in_redirect_delivery(auth_client, client):
    """Test redirect when delivery agent is already logged in."""
    auth_client.login('1234567897', 'driver123', 'Delivery Agent')
    response = client.get(url_for('main.login'), follow_redirects=True)
    assert b'Delivery Dashboard' in response.data

"""
This test file covers:

    Testing the index route
    Testing the login route with GET method
    Testing successful login for all user types (admin, manager, customer, delivery agent)
    Testing login with invalid credentials (wrong password, wrong phone, mismatched user type)
    Testing the logout route
    Testing redirects when a user is already logged in
"""