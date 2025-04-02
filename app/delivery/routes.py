from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.delivery import delivery
from app.models.stores import stores, orders
from app.models.users import users

@delivery.route('/dashboard')
@login_required
def delivery_agent_dashboard():
    if current_user.user_type != "Delivery Agent":
        flash('Access denied', 'danger')
        return redirect(url_for('main.login'))

    assigned_orders = [o for o in orders.values() 
                      if o['delivery_agent'] == current_user.id 
                      and not o['delivered']]
    
    print("Assigned orders:", assigned_orders)
    return render_template('delivery/dashboard.html',
                         orders=assigned_orders,
                         stores=stores)

@delivery.route('/mark_delivered/<order_id>', methods=['POST'])
@login_required
def mark_delivered(order_id):
    if current_user.user_type != "Delivery Agent":
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.login'))

    order = orders.get(order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('delivery.delivery_agent_dashboard'))

    if order["delivery_agent"] != current_user.id:
        flash('This order is not assigned to you.', 'danger')
        return redirect(url_for('delivery.delivery_agent_dashboard'))

    order["delivered"] = True
    customer_location = order["customer_location"]

    for user in users:
        if user["username"] == current_user.id:
            user["location"] = customer_location
            break

    flash('Order marked as delivered!', 'success')
    return redirect(url_for('delivery.delivery_agent_dashboard'))

@delivery.route('/update_order_status/<order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = orders.get(order_id)
    if not order or order['delivery_agent'] != current_user.id:
        flash('Invalid request', 'danger')
        return redirect(url_for('delivery.delivery_agent_dashboard'))

    new_status = request.form.get('status')
    
    if new_status == 'collected':
        order['status'] = 'collected'
    elif new_status == 'delivered':
        order['status'] = 'delivered'
        order['delivered'] = True
        for user in users:
            if user['username'] == current_user.id:
                user['location'] = order['customer_location']
                break
    
    flash(f'Order status updated to {new_status}', 'success')
    return redirect(url_for('delivery.delivery_agent_dashboard'))

@delivery.route('/completed_deliveries')
@login_required
def completed_deliveries():
    if current_user.user_type != "Delivery Agent":
        flash('Access denied', 'danger')
        return redirect(url_for('main.login'))
    
    completed_deliveries = {order_id: order for order_id, order in orders.items() 
                        if order.get('delivery_agent') == current_user.id 
                        and order.get('status') == 'delivered'}
    
    return render_template('delivery/completed_deliveries.html',
                           title='Completed Deliveries',
                           completed_deliveries=completed_deliveries,
                           stores=stores)


