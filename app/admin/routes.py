from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.admin import admin
from app.models.stores import stores, orders
from app.models.users import users

@admin.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type != "Admin":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.login'))

    delivery_agents = [user for user in users if user['user_type'] == 'Delivery Agent']
    stores_list = stores

    return render_template('admin/dashboard.html',
                           title='Admin Dashboard',
                           stores=stores_list,
                           delivery_agents=delivery_agents)

@admin.route('/store_details/<int:store_id>')
@login_required
def store_details(store_id):
    if current_user.user_type != "Admin":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.login'))

    store = stores.get(store_id)
    if not store:
        flash('Store not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    manager = next((user for user in users if user.get('store_id') == store_id and user['user_type'] == 'Manager'), None)

    return render_template('admin/store_details.html',
                           title='Store Details',
                           store=store,
                           manager=manager)

@admin.route('/delivery_agent_details/<agent_id>')
@login_required
def delivery_agent_details(agent_id):
    if current_user.user_type != "Admin":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.login'))

    delivery_agent = next((user for user in users if user['username'] == agent_id and user['user_type'] == 'Delivery Agent'), None)

    if not delivery_agent:
        flash('Delivery agent not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('delivery/delivery_agent_details.html',
                           title='Delivery Agent Details',
                           agent=delivery_agent)

@admin.route('/orders')
@login_required
def admin_orders():
    if current_user.user_type != "Admin":
        flash('Access denied', 'danger')
        return redirect(url_for('main.login'))
    return render_template('orders.html', title='All Orders', orders=orders, stores=stores)
