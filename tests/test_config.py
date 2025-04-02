import pytest
from app import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig

def test_development_config():
    """Test development configuration."""
    app = create_app('development')
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False
    assert app.config['SECRET_KEY'] is not None

def test_production_config():
    """Test production configuration."""
    app = create_app('production')
    assert app.config['DEBUG'] is False
    assert app.config['TESTING'] is False
    assert app.config['SECRET_KEY'] is not None

def test_testing_config():
    """Test testing configuration."""
    app = create_app('testing')
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] is not None
    assert app.config['WTF_CSRF_ENABLED'] is False

def test_default_config():
    """Test default configuration (should be development)."""
    app = create_app()
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False
    assert app.config['SECRET_KEY'] is not None

def test_config_from_object():
    """Test loading config from object."""
    app = create_app()
    app.config.from_object(TestingConfig)
    assert app.config['TESTING'] is True

def test_environment_variable_config(monkeypatch):
    """Test loading config from environment variable."""
    # Set environment variable
    monkeypatch.setenv('SECRET_KEY', 'test_secret_key')
    
    app = create_app()
    assert app.config['SECRET_KEY'] == 'test_secret_key'

def test_invalid_config():
    """Test handling of invalid configuration name."""
    # This should fall back to default config
    app = create_app('invalid_config_name')
    assert app.config['DEBUG'] is True  # Default is development, which has DEBUG=True


"""
    Testing that each configuration environment (development, production, testing) loads with the correct settings
    Verifying that the default configuration is set to development
    Testing that configuration can be loaded from an object
    Testing that environment variables are properly loaded into the configuration
    Testing the handling of invalid configuration names
"""