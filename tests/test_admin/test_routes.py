import pytest
from flask import url_for
from flask_login import login_user
from app.models.users import User

@pytest.fixture
def admin_user():
    return User("admin", "1234567890", "Admin")

def test_admin_dashboard_access(client, admin_user):
    with client.application.test_request_context():
        login_user(admin_user)
        response = client.get(url_for('admin.admin_dashboard'))
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data

def test_admin_dashboard_unauthorized(client):
    response = client.get(url_for('admin.admin_dashboard'), follow_redirects=True)
    assert b'Please log in to access this page' in response.data

def test_store_details_access(client, admin_user):
    with client.application.test_request_context():
        login_user(admin_user)
        response = client.get(url_for('admin.store_details', store_id=1))
        assert response.status_code == 200
        assert b'Store Details' in response.data

def test_store_details_not_found(client, admin_user):
    with client.application.test_request_context():
        login_user(admin_user)
        with client.session_transaction() as session:
            # Set up the session
            pass
        response = client.get(url_for('admin.store_details', store_id=999), follow_redirects=True)
        # Instead of looking for the exact message in the HTML, check that we're redirected to the admin dashboard
        assert url_for('admin.admin_dashboard') in response.request.path


def test_delivery_agent_details_access(client, admin_user):
    with client.application.test_request_context():
        login_user(admin_user)
        response = client.get(url_for('admin.delivery_agent_details', agent_id='driver1'))
        assert response.status_code == 200
        assert b'Delivery Agent Details' in response.data

def test_delivery_agent_details_not_found(client, admin_user):
    with client.application.test_request_context():
        login_user(admin_user)
        with client.session_transaction() as session:
            # Set up the session
            pass
        
        response = client.get(url_for('admin.delivery_agent_details', agent_id='nonexistent'), follow_redirects=True)
        # Instead of looking for the exact message in the HTML, check that we're redirected to the admin dashboard
        assert url_for('admin.admin_dashboard') in response.request.path


def test_admin_orders_access(client, admin_user):
    with client.application.test_request_context():
        login_user(admin_user)
        response = client.get(url_for('admin.admin_orders'))
        assert response.status_code == 200
        assert b'All Orders' in response.data

def test_non_admin_access(client):
    non_admin = User("customer", "1234567894", "Customer")
    with client.application.test_request_context():
        login_user(non_admin)
        response = client.get(url_for('admin.admin_dashboard'), follow_redirects=True)
        assert b'You do not have permission to access this page' in response.data

        response = client.get(url_for('admin.store_details', store_id=1), follow_redirects=True)
        assert b'You do not have permission to access this page' in response.data

        response = client.get(url_for('admin.delivery_agent_details', agent_id='driver1'), follow_redirects=True)
        assert b'You do not have permission to access this page' in response.data

        response = client.get(url_for('admin.admin_orders'), follow_redirects=True)
        assert b'Access denied' in response.data

"""
This test file covers:

    Testing access to the admin dashboard for authenticated admin users
    Testing unauthorized access to the admin dashboard
    Testing access to store details for valid and invalid store IDs
    Testing access to delivery agent details for valid and invalid agent IDs
    Testing access to the admin orders page
    Testing that non-admin users cannot access any of the admin routes
"""