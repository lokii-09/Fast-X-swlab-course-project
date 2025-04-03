from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
from app.customer import customer
from app.models.stores import stores, orders, generate_order_id
from app.models.users import users, FAKE_BANK_ACCOUNTS
from app.utils.algo import assign_driver
from datetime import datetime

@customer.route('/dashboard')
@login_required
def customer_dashboard():
    if current_user.user_type != "Customer":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.login'))
    
    search_term = request.args.get('search', '').lower()
    
    all_items = {}
    for store_id, store in stores.items():
        for item_name, item_details in store["items"].items():
            if item_details["stock"] > 0:
                price_after_discount = item_details["price"] * (1 - item_details["discount"] / 100)
                if (item_name not in all_items or 
                    price_after_discount < all_items[item_name]["final_price"] or
                    (price_after_discount == all_items[item_name]["final_price"] and 
                    item_details["stock"] > all_items[item_name]["stock"])):
                    all_items[item_name] = {
                        "name": item_name,
                        "type": item_details["item_type"],
                        "price": item_details["price"],
                        "discount": item_details["discount"],
                        "final_price": price_after_discount,
                        "stock": item_details["stock"],
                        "store_id": store_id,
                        "store_location": store["location"],
                    }

    items_list = list(all_items.values())
    if search_term:
        items_list = [item for item in items_list if search_term in item["name"].lower() or search_term in item["type"].lower()]

    return render_template('customer/dashboard.html',
                           title='Customer Dashboard',
                           items=items_list,
                           search_term=search_term)

@customer.route('/add_to_cart/<item_name>')
@login_required
def add_to_cart(item_name):
    # Find the item (inefficient, but works with the dummy data)
    item_to_add = None
    store_id_to_use = None  # Store the store_id

    for store_id, store in stores.items():
        if item_name in store["items"]:
            item_details = store["items"][item_name]
            price_after_discount = item_details["price"] * (1 - item_details["discount"] / 100)

            if item_to_add is None or price_after_discount < item_to_add["final_price"]:
                item_to_add = {
                    "name": item_name,
                    "type": item_details["item_type"],
                    "price": item_details["price"],
                    "discount": item_details["discount"],
                    "final_price": price_after_discount,
                    "stock": item_details["stock"],
                    "store_id": store_id,
                    "store_location": store["location"],
                }
                store_id_to_use = store_id  # Save the store_id

    if item_to_add:
        # Check if item is in stock
        if stores[store_id_to_use]["items"][item_name]["stock"] <= 0:
            flash(f'{item_name} is out of stock!', 'danger')
            return redirect(url_for('customer.customer_dashboard'))

        # Initialize cart in session if it doesn't exist
        if 'cart' not in session:
            session['cart'] = {}

        cart = session['cart']
        if item_name in cart:
            # Check if adding more exceeds stock
            if cart[item_name]['quantity'] < stores[store_id_to_use]["items"][item_name]["stock"]:
                cart[item_name]['quantity'] += 1
            else:
                flash(f'Cannot add more {item_name}.  Maximum stock reached!', 'warning')
                return redirect(url_for('customer.customer_dashboard'))
        else:
            item_to_add['quantity'] = 1
            cart[item_name] = item_to_add

        session['cart'] = cart  # Update the session
        session.modified = True # Ensure session is updated
        flash(f'{item_name} added to cart!', 'success')
    else:
        flash('Item not found.', 'danger')

    return redirect(url_for('customer.customer_dashboard'))

@customer.route('/cart')
@login_required
def view_cart():
    # Ensure cart exists in session
    if 'cart' not in session:
        session['cart'] = {}
    
    cart_items = session.get('cart', {})
    subtotal = sum(item['final_price'] * item['quantity'] for item in cart_items.values())
    return render_template('customer/cart.html', subtotal=subtotal)

@customer.route('/remove_item/<item_name>', methods=['POST'])
@login_required
def remove_item(item_name):
    cart = session.get('cart', {})
    if item_name in cart:
        del cart[item_name]
        session['cart'] = cart
        session.modified = True
        flash(f'{item_name} removed from cart.', 'success')
    else:
        flash('Item not found in cart.', 'danger')
    return redirect(url_for('customer.view_cart'))

@customer.route('/clear_cart')
@login_required
def clear_cart():
    session['cart'] = {}
    session.modified = True
    flash('Cart cleared.', 'info')
    return redirect(url_for('customer.view_cart'))

@customer.route('/update_cart/<item_name>', methods=['POST'])
@login_required
def update_cart(item_name):
    action = request.form.get('action')
    cart = session.get('cart', {})

    # Find the store_id for the item
    store_id_to_use = None
    for store_id, store in stores.items():
        if item_name in store["items"]:
            store_id_to_use = store_id
            break

    if item_name in cart:
        if action == 'increase':
            # Check if adding more exceeds stock
            if cart[item_name]['quantity'] < stores[store_id_to_use]["items"][item_name]["stock"]:
                cart[item_name]['quantity'] += 1
            else:
                flash(f'Cannot add more {item_name}. Maximum stock reached!', 'warning')
                return redirect(url_for('customer.view_cart'))
        elif action == 'decrease':
            cart[item_name]['quantity'] -= 1
            if cart[item_name]['quantity'] <= 0:
                del cart[item_name]  # Remove item if quantity is 0
                session['cart'] = cart
        session.modified = True
    else:
        flash('Item not found in cart.', 'danger')

    return redirect(url_for('customer.view_cart'))

@customer.route('/process_purchase', methods=['POST'])
@login_required
def process_purchase():
    payment_method = request.form.get('payment_method')

    if not payment_method:
        flash('Please select a payment method.', 'danger')
        return redirect(url_for('customer.view_cart'))
    
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer.customer_dashboard'))

    subtotal = sum(item['final_price'] * item['quantity'] for item in cart.values())

    # Payment Processing with Balance Check
    payment_success = False
    
    if payment_method == "card":
        card_number = request.form.get("card_number")
        expiry = request.form.get("expiry")
        cvv = request.form.get("cvv")

        if not card_number or not expiry or not cvv:
            flash("Please enter card details.", "danger")
            return redirect(url_for("customer.view_cart"))

        # Verify card details
        if card_number not in FAKE_BANK_ACCOUNTS["card"] or \
           FAKE_BANK_ACCOUNTS["card"][card_number]["expiry"] != expiry or \
           FAKE_BANK_ACCOUNTS["card"][card_number]["cvv"] != cvv:
            flash("Invalid card details.", "danger")
            return redirect(url_for("customer.view_cart"))

        # Check balance
        if FAKE_BANK_ACCOUNTS["card"][card_number]["balance"] < subtotal:
            flash(f"Insufficient balance. You need ${subtotal} but your balance is ${FAKE_BANK_ACCOUNTS['card'][card_number]['balance']}.", "danger")
            return redirect(url_for("customer.view_cart"))

        # Process payment
        FAKE_BANK_ACCOUNTS["card"][card_number]["balance"] -= subtotal
        payment_success = True
        flash(f"Payment successful! Remaining balance: ${FAKE_BANK_ACCOUNTS['card'][card_number]['balance']}", "success")

    elif payment_method == "upi":
        upi_id = request.form.get("upi_id")
        if not upi_id:
            flash("Please enter UPI ID.", "danger")
            return redirect(url_for("customer.view_cart"))

        # Verify UPI ID
        if upi_id not in FAKE_BANK_ACCOUNTS["upi"]:
            flash("Invalid UPI ID.", "danger")
            return redirect(url_for("customer.view_cart"))

        # Check balance
        if FAKE_BANK_ACCOUNTS["upi"][upi_id]["balance"] < subtotal:
            flash(f"Insufficient balance. You need ${subtotal} but your balance is ${FAKE_BANK_ACCOUNTS['upi'][upi_id]['balance']}.", "danger")
            return redirect(url_for("customer.view_cart"))

        # Process payment
        FAKE_BANK_ACCOUNTS["upi"][upi_id]["balance"] -= subtotal
        payment_success = True
        flash(f"Payment successful! Remaining balance: ${FAKE_BANK_ACCOUNTS['upi'][upi_id]['balance']}", "success")

    elif payment_method == "cod":
        payment_success = True
        flash("Cash on Delivery selected. You will pay $" + str(subtotal) + " upon delivery.", "info")

    else:
        flash("Invalid payment method.", "danger")
        return redirect(url_for("customer.view_cart"))
    
    if not payment_success:
        flash("Payment processing failed.", "danger")
        return redirect(url_for ("customer.view_cart"))
    
    # Create order structure
    order_id = generate_order_id()
    customer_location = None
    for user in users:
        if user['username'] == current_user.id:
            customer_location = user.get('location')
            break
    
    # Group cart items by store
    items_by_store = {}
    for item_name, item in cart.items():
        store_id = item['store_id']
        if store_id not in items_by_store:
            items_by_store[store_id] = {}
        items_by_store[store_id][item_name] = item['quantity']

    # Create order object for driver assignment
    order = {
        "order_id": order_id,
        "customer_id": current_user.id,
        "customer_location": customer_location,
        "items_by_store": items_by_store,
    }
    
    # Assign driver using Dijkstra's algorithm and get optimized store order
    assigned_driver, optimized_store_order = assign_driver(order)
    
    if assigned_driver:
        flash(f"Order placed successfully! Assigned to {assigned_driver}.", 'success')
    else:
        flash("Order placed successfully! No drivers available at this moment.", 'warning')
    
    # Create new order in the orders dictionary with optimized store order
    orders[order_id] = {
        "order_id": order_id,
        "customer_id": current_user.id,
        "customer_location": customer_location,
        "items_by_store": items_by_store,
        "optimized_store_order": optimized_store_order,  # Add the optimized store order
        "delivery_agent": assigned_driver,
        "status": "processing",
        "delivered": False,
        "timestamp": datetime.now().isoformat(),
        "payment_method": payment_method,
        "total_amount": subtotal
    }

    # Reduce Stock and prepare order details for email
    order_details = ""
    
    # Use optimized store order if available, otherwise use regular order
    store_visit_order = optimized_store_order if optimized_store_order else list(items_by_store.keys())
    
    # Process items in the optimized store order
    for store_id in store_visit_order:
        if store_id in items_by_store:
            store_items = items_by_store[store_id]
            order_details += f"\nFrom {stores[store_id]['name']}:\n"
            for item_name, quantity in store_items.items():
                # Find the item in the cart to get its details
                for cart_item_name, cart_item in cart.items():
                    if cart_item_name == item_name and cart_item['store_id'] == store_id:
                        stores[store_id]["items"][item_name]["stock"] -= quantity
                        order_details += f"- {item_name} (Qty: {quantity})\n"
                        break

    """
    # Send order confirmation email
    customer_email = None
    for user in users:
        if user['username'] == current_user.id and 'email' in user:
            customer_email = user['email']
            break
    
    if customer_email:
        try:
            send_order_confirmation_email(customer_email, order_id, order_details, subtotal)
            flash("Order confirmation email sent!", "info")
        except Exception as e:
            print(f"Email error: {e}")
            flash("Could not send confirmation email.", "warning")
    """
    
    session['cart'] = {}  # Clear the cart
    session.modified = True

    return redirect(url_for('customer.customer_orders'))  # Redirect to orders page to see the new order

@customer.route('/track_order/<order_id>')
@login_required
def track_order(order_id):
    order = orders.get(order_id)
    if not order or order['customer_id'] != current_user.id:
        flash('Order not found', 'danger')
        return redirect(url_for('customer.customer_dashboard'))
    
    delivery_agent = next((u for u in users if u['username'] == order['delivery_agent']), None)
    return render_template('customer/track_order.html', 
                         order=order,
                         delivery_agent=delivery_agent,
                         stores=stores)

@customer.route('/orders')
@login_required
def customer_orders():
    if current_user.user_type != "Customer":
        flash('Access denied', 'danger')
        return redirect(url_for('main.login'))
    
    customer_orders = {order_id: order for order_id, order in orders.items()
                      if order.get('customer_id') == current_user.id}
    
    return render_template('orders.html',
                          title='Your Orders',
                          orders=customer_orders,
                          stores=stores)
