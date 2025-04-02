from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import config
import os

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_message_category = 'info'

def create_app(config_name='default'):
    app = Flask(__name__)
    
    try:
        app.config.from_object(config[config_name])
    except KeyError:
        # Fall back to default config if invalid name provided
        app.config.from_object(config['default'])
    
    if os.environ.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    
    # Initialize extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Set login view based on blueprint
    login_manager.login_view = 'main.login'
    
    # Register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from app.manager import manager as manager_blueprint
    app.register_blueprint(manager_blueprint, url_prefix='/manager')
    
    from app.customer import customer as customer_blueprint
    app.register_blueprint(customer_blueprint, url_prefix='/customer')
    
    from app.delivery import delivery as delivery_blueprint
    app.register_blueprint(delivery_blueprint, url_prefix='/delivery')
    
    # Import User model for login manager
    from app.models.users import User
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.users import users
        for user_data in users:
            if user_data['username'] == user_id:
                if user_data['user_type'] == "Manager":
                    return User(user_data['username'], user_data['phone'], user_data['user_type'], user_data.get('store_id'))
                elif user_data['user_type'] == "Delivery Agent":
                    return User(user_data['username'], user_data['phone'], user_data['user_type'], rating=user_data.get('rating'), location=user_data.get('location'))
                return User(user_data['username'], user_data['phone'], user_data['user_type'], email=user_data.get('email'), location=user_data.get('location'))
        return None
    
    return app
