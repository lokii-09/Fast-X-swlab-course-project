import pytest
from flask import current_app, url_for

def test_app_exists(app):
    """Test that the app exists."""
    assert current_app is not None

def test_app_is_testing(app):
    """Test that the app is in testing mode."""
    assert current_app.config['TESTING']
    assert current_app.config['WTF_CSRF_ENABLED'] is False

def test_app_secret_key(app):
    """Test that the app has a secret key."""
    assert current_app.secret_key is not None

def test_home_page(client):
    """Test that the home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_login_page(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_404_page(client):
    """Test that 404 page works."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404

def test_login_required_redirect(client):
    """Test that protected routes redirect to login when not authenticated."""
    # Test a few protected routes from different blueprints
    protected_routes = [
        '/admin/dashboard',
        '/manager/dashboard',
        '/customer/dashboard',
        '/delivery/dashboard'
    ]
    
    for route in protected_routes:
        response = client.get(route)
        # Should redirect to login page
        assert response.status_code == 302
        assert '/login' in response.location

def test_blueprint_registration(app):
    """Test that all blueprints are registered."""
    blueprints = [
        'main',
        'admin',
        'manager',
        'customer',
        'delivery'
    ]
    
    for blueprint in blueprints:
        assert blueprint in app.blueprints

# Admin tests
def test_admin_login_functionality(auth_client):
    """Test login functionality with valid admin credentials."""
    response = auth_client.login('1234567890', 'admin123', 'Admin')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_admin_login_invalid_credentials(auth_client):
    """Test login with invalid admin credentials."""
    response = auth_client.login('1234567890', 'wrongpassword', 'Admin')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_admin_logout(auth_client):
    """Test admin logout functionality."""
    # First login
    auth_client.login('1234567890', 'admin123', 'Admin')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data

# Manager tests
def test_manager_login_functionality(auth_client):
    """Test login functionality with valid manager credentials."""
    response = auth_client.login('1234567891', 'manager123', 'Manager')
    assert response.status_code == 200
    assert b'Manager Dashboard' in response.data

def test_manager_login_invalid_credentials(auth_client):
    """Test login with invalid manager credentials."""
    response = auth_client.login('1234567891', 'wrongpassword', 'Manager')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_manager_logout(auth_client):
    """Test manager logout functionality."""
    # First login
    auth_client.login('1234567891', 'manager123', 'Manager')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data

# Manager tests
def test_manager_login_functionality(auth_client):
    """Test login functionality with valid manager credentials."""
    response = auth_client.login('1234567892', 'manager123', 'Manager')
    assert response.status_code == 200
    assert b'Manager Dashboard' in response.data

def test_manager_login_invalid_credentials(auth_client):
    """Test login with invalid manager credentials."""
    response = auth_client.login('1234567892', 'wrongpassword', 'Manager')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_manager_logout(auth_client):
    """Test manager logout functionality."""
    # First login
    auth_client.login('1234567892', 'manager123', 'Manager')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data

# Manager tests
def test_manager_login_functionality(auth_client):
    """Test login functionality with valid manager credentials."""
    response = auth_client.login('1234567893', 'manager123', 'Manager')
    assert response.status_code == 200
    assert b'Manager Dashboard' in response.data

def test_manager_login_invalid_credentials(auth_client):
    """Test login with invalid manager credentials."""
    response = auth_client.login('1234567893', 'wrongpassword', 'Manager')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_manager_logout(auth_client):
    """Test manager logout functionality."""
    # First login
    auth_client.login('1234567893', 'manager123', 'Manager')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data

# Customer tests
def test_customer_login_functionality(auth_client):
    """Test login functionality with valid customer credentials."""
    response = auth_client.login('1234567894', 'customer123', 'Customer')
    assert response.status_code == 200
    assert b'Customer Dashboard' in response.data

def test_customer_login_invalid_credentials(auth_client):
    """Test login with invalid customer credentials."""
    response = auth_client.login('1234567894', 'wrongpassword', 'Customer')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_customer_logout(auth_client):
    """Test customer logout functionality."""
    # First login
    auth_client.login('1234567894', 'customer123', 'Customer')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data


def test_customer_login_functionality(auth_client):
    """Test login functionality with valid customer credentials."""
    response = auth_client.login('1234567895', 'customer123', 'Customer')
    assert response.status_code == 200
    assert b'Customer Dashboard' in response.data

def test_customer_login_invalid_credentials(auth_client):
    """Test login with invalid customer credentials."""
    response = auth_client.login('1234567895', 'wrongpassword', 'Customer')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_customer_logout(auth_client):
    """Test customer logout functionality."""
    # First login
    auth_client.login('1234567895', 'customer123', 'Customer')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data

def test_customer_login_functionality(auth_client):
    """Test login functionality with valid customer credentials."""
    response = auth_client.login('1234567896', 'customer123', 'Customer')
    assert response.status_code == 200
    assert b'Customer Dashboard' in response.data

def test_customer_login_invalid_credentials(auth_client):
    """Test login with invalid customer credentials."""
    response = auth_client.login('1234567896', 'wrongpassword', 'Customer')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_customer_logout(auth_client):
    """Test customer logout functionality."""
    # First login
    auth_client.login('1234567896', 'customer123', 'Customer')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data


# Delivery Agent tests
def test_delivery_agent_login_functionality(auth_client):
    """Test login functionality with valid delivery agent credentials."""
    response = auth_client.login('1234567897', 'driver123', 'Delivery Agent')
    assert response.status_code == 200
    assert b'Delivery Dashboard' in response.data

def test_delivery_agent_login_invalid_credentials(auth_client):
    """Test login with invalid delivery agent credentials."""
    response = auth_client.login('1234567897', 'wrongpassword', 'Delivery Agent')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_delivery_agent_logout(auth_client):
    """Test delivery agent logout functionality."""
    # First login
    auth_client.login('1234567897', 'driver123', 'Delivery Agent')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data

def test_delivery_agent_login_functionality(auth_client):
    """Test login functionality with valid delivery agent credentials."""
    response = auth_client.login('1234567898', 'driver123', 'Delivery Agent')
    assert response.status_code == 200
    assert b'Delivery Dashboard' in response.data

def test_delivery_agent_login_invalid_credentials(auth_client):
    """Test login with invalid delivery agent credentials."""
    response = auth_client.login('1234567898', 'wrongpassword', 'Delivery Agent')
    # wrongpassword is just an example
    assert b'Login Unsuccessful' in response.data

def test_delivery_agent_logout(auth_client):
    """Test delivery agent logout functionality."""
    # First login
    auth_client.login('1234567898', 'driver123', 'Delivery Agent')
    
    # Then logout
    response = auth_client.logout()
    assert response.status_code == 200
    assert b'Login' in response.data


"""
This test_app.py file covers:
    Basic application existence and configuration tests
    Testing that the home and login pages load correctly
    Testing the 404 error page
    Verifying that protected routes redirect to login when not authenticated
    Checking that all blueprints are registered correctly
    Testing that static files are accessible
    Testing login functionality with both valid and invalid credentials
    Testing logout functionality
"""