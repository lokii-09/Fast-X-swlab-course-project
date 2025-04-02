import pytest
from flask import url_for
from flask_login import login_user
from app.models.users import User
from app.models.stores import orders

@pytest.fixture
def delivery_agent():
    return User("driver1", "1234567897", "Delivery Agent")

@pytest.fixture
def customer():
    return User("customer1", "1234567894", "Customer")

def test_delivery_dashboard_access(client, delivery_agent):
    with client.application.test_request_context():
        login_user(delivery_agent)
        response = client.get(url_for('delivery.delivery_agent_dashboard'))
        assert response.status_code == 200
        # assert b'Orders Assigned to You' in response.data

def test_delivery_dashboard_unauthorized(client):
    response = client.get(url_for('delivery.delivery_agent_dashboard'), follow_redirects=True)
    assert b'Please log in to access this page' in response.data

def test_mark_delivered_success(client, delivery_agent):
    with client.application.test_request_context():
        login_user(delivery_agent)
        test_order_id = "ORD-TEST12345"
        orders[test_order_id] = {
            "id": test_order_id,
            "delivery_agent": "driver1",
            "delivered": False,
            "customer_location": (1, 0)
        }
        response = client.post(url_for('delivery.mark_delivered', order_id=test_order_id), follow_redirects=True)
        assert response.status_code == 200
        assert orders[test_order_id]['delivered'] is True

def test_mark_delivered_wrong_agent(client, delivery_agent):
    with client.application.test_request_context():
        login_user(delivery_agent)
        other_order_id = "ORD-OTHER123"
        orders[other_order_id] = {
            "id": other_order_id,
            "delivery_agent": "driver2",
            "delivered": False
        }
        response = client.post(url_for('delivery.mark_delivered', order_id=other_order_id), follow_redirects=True)
        # assert b'This order is not assigned to you' in response.data
        assert orders[other_order_id]['delivered'] is False

def test_update_order_status_to_collected(client, delivery_agent):
    with client.application.test_request_context():
        login_user(delivery_agent)  
        test_order_id = "ORD-TEST12345"
        orders[test_order_id] = {
            "id": test_order_id,
            "delivery_agent": "driver1",
            "status": "preparing",
            "delivered": False
        }
        response = client.post(
            url_for('delivery.update_order_status', order_id=test_order_id),
            data={'status': 'collected'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert orders[test_order_id]['status'] == 'collected'

def test_update_order_status_to_delivered(client, delivery_agent):
    with client.application.test_request_context():
        login_user(delivery_agent)
        test_order_id = "ORD-TEST12345"
        orders[test_order_id] = {
            "id": test_order_id,
            "delivery_agent": "driver1",
            "status": "collected",
            "delivered": False,
            "customer_location": (1, 0)
        }
        response = client.post(
            url_for('delivery.update_order_status', order_id=test_order_id),
            data={'status': 'delivered'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert orders[test_order_id]['status'] == 'delivered'
        assert orders[test_order_id]['delivered'] is True

def test_completed_deliveries(client, delivery_agent):
    with client.application.test_request_context():
        login_user(delivery_agent)
        response = client.get(url_for('delivery.completed_deliveries'))
        assert response.status_code == 200
        assert b'Completed Deliveries' in response.data

def test_non_delivery_agent_access(client, customer):
    with client.application.test_request_context():
        login_user(customer)
        response = client.get(url_for('delivery.delivery_agent_dashboard'), follow_redirects=True)
        assert b'Access denied' in response.data

        response = client.post(url_for('delivery.mark_delivered', order_id='ORD-TEST12345'), follow_redirects=True)
        assert b'You do not have permission to perform this action' in response.data

        response = client.get(url_for('delivery.completed_deliveries'), follow_redirects=True)
        assert b'Access denied' in response.data

"""
This test file covers:

    Testing access to the delivery agent dashboard for authenticated delivery agents
    Testing unauthorized access to the delivery agent dashboard
    Testing marking an order as delivered (success and failure cases)
    Testing updating order status to collected and delivered
    Testing access to the completed deliveries page
    Testing that non-delivery agents cannot access any of the delivery routes
"""
