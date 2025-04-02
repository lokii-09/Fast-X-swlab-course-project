from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.manager import manager
from app.models.stores import stores, orders
from app.forms import AddItemForm, UpdateItemForm

@manager.route('/dashboard')
@login_required
def manager_dashboard():
    # Check if user is a manager
    if current_user.user_type != "Manager":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.login'))
    
    # Find the store associated with the logged-in manager
    if current_user.id == 'manager1':
        store = stores[1]
    elif current_user.id == 'manager2':
        store = stores[2]
    elif current_user.id == 'manager3':
        store = stores[3]
    else:
        return redirect(url_for('main.login'))
    
    if not store:
        flash('No store found for this manager.', 'danger')
        return redirect(url_for('main.login'))
    
    # Get items for this store
    store_items = store["items"] if "items" in store else []
    
    return render_template(
        'manager/dashboard.html',
        title='Manager Dashboard',
        store=store,
        items=store_items
    )

@manager.route('/orders')
@login_required
def manager_orders():
    if current_user.user_type != "Manager":
        flash('Access denied', 'danger')
        return redirect(url_for('main.login'))
    
    # Find the store associated with the logged-in manager
    store_id = None
    if current_user.id == 'manager1':
        store_id = 1
    elif current_user.id == 'manager2':
        store_id = 2
    elif current_user.id == 'manager3':
        store_id = 3
    
    if not store_id:
        flash('No store associated with this manager', 'warning')
        return redirect(url_for('manager.manager_dashboard'))
    
    store_orders = {order_id: order for order_id, order in orders.items() if store_id in order['items_by_store']}
    return render_template('orders.html', title='Store Orders', orders=store_orders, stores=stores)

@manager.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.user_type != "Manager":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.login'))
    
    form = AddItemForm()
    
    if form.validate_on_submit():
        # Find the store associated with the logged-in manager
        store_id = None
        if current_user.id == 'manager1':
            store_id = 1
        elif current_user.id == 'manager2':
            store_id = 2
        elif current_user.id == 'manager3':
            store_id = 3
        
        if not store_id:
            flash('Store not found for this manager.', 'danger')
            return redirect(url_for('manager.manager_dashboard'))
        
        # Get form data
        item_name = form.item_name.data
        item_type = form.item_type.data
        price = form.price.data
        stock = form.stock.data
        discount = form.discount.data
        
        # Check if item already exists in the store
        if item_name in stores[store_id]["items"]:
            flash(f'Item "{item_name}" already exists in your store.', 'warning')
            return redirect(url_for('manager.add_item'))
        
        # Add the new item to the store
        stores[store_id]["items"][item_name] = {
            "price": price,
            "stock": stock,
            "discount": discount,
            "item_type": item_type
        }
        
        flash(f'Item "{item_name}" has been added successfully!', 'success')
        return redirect(url_for('manager.manager_dashboard'))
    
    return render_template('manager/add_item.html', title='Add New Item', form=form)

@manager.route('/update_item/<item_name>', methods=['GET', 'POST'])
@login_required
def update_item(item_name):
    if current_user.user_type != "Manager":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.login'))
    
    # Find the store associated with the logged-in manager
    store_id = None
    if current_user.id == 'manager1':
        store_id = 1
    elif current_user.id == 'manager2':
        store_id = 2
    elif current_user.id == 'manager3':
        store_id = 3
    
    if not store_id:
        flash('Store not found for this manager.', 'danger')
        return redirect(url_for('manager.manager_dashboard'))
    
    # Check if the item exists in the store
    if item_name not in stores[store_id]["items"]:
        flash(f'Item "{item_name}" not found in your store.', 'danger')
        return redirect(url_for('manager.manager_dashboard'))
    
    item = stores[store_id]["items"][item_name]
    form = UpdateItemForm()
    
    # Pre-populate the form with current values
    if request.method == 'GET':
        form.price.data = item["price"]
        form.stock.data = item["stock"]
        form.discount.data = item["discount"]
    
    if form.validate_on_submit():
        # Update the item details
        stores[store_id]["items"][item_name]["price"] = form.price.data
        stores[store_id]["items"][item_name]["stock"] = form.stock.data
        stores[store_id]["items"][item_name]["discount"] = form.discount.data
        
        flash(f'Item "{item_name}" has been updated successfully!', 'success')
        return redirect(url_for('manager.manager_dashboard'))
    
    return render_template('manager/update_item.html', 
                          title='Update Item',
                          form=form,
                          item_name=item_name,
                          item_type=item["item_type"])
