from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.main import main
from app.forms import LoginForm
from app import bcrypt
from app.models.users import users, User

@main.route('/')
def index():
    return render_template('main/home.html', title='Welcome to FastX')

@main.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to the user's respective dashboard
    if current_user.is_authenticated:
        if current_user.user_type == "Admin":
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.user_type == "Manager":
            return redirect(url_for('manager.manager_dashboard'))
        elif current_user.user_type == "Customer":
            return redirect(url_for('customer.customer_dashboard'))
        elif current_user.user_type == "Delivery Agent":
            return redirect(url_for('delivery.delivery_agent_dashboard'))
        else:
            return redirect(url_for('main.index'))
            
    form = LoginForm()
    if form.validate_on_submit():
        for user_data in users:
            if user_data['phone'] == form.phone.data and user_data['user_type'] == form.user_type.data:
                if bcrypt.check_password_hash(user_data['password'], form.password.data):
                    user = User(user_data['username'], user_data['phone'], user_data['user_type'], 
                               user_data.get('store_id'), user_data.get('rating'))
                    login_user(user, remember=form.remember.data)
                    
                    if user.user_type == "Admin":
                        return redirect(url_for('admin.admin_dashboard'))
                    elif user.user_type == "Manager":
                        return redirect(url_for('manager.manager_dashboard'))
                    elif user.user_type == "Customer":
                        return redirect(url_for('customer.customer_dashboard'))
                    elif user.user_type == "Delivery Agent":
                        return redirect(url_for('delivery.delivery_agent_dashboard'))
                    else:
                        return redirect(url_for('main.index'))
        
        flash('Login Unsuccessful. Please check phone number and password.', 'danger')
    
    return render_template('main/login.html', title='Login', form=form)

@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


