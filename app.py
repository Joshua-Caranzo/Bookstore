from flask import Flask,render_template,request,redirect,url_for,flash,session, jsonify
from flask import current_app as app
from dbhelper import *
from datetime import datetime

app = Flask(__name__)
app.secret_key = "!@#$%"

@app.route("/login", methods=['POST', 'GET'])
def login():
    email = ''
    password = ''
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        # set a static user validation
        user = getuser('users', email=email, password=password)
        customer = getrecord('customers', email=email)
        
        if len(user) > 0:
            if email == "admin@gmail.com" and password == "1234":
                session['name'] = user[0]['id'] 
                flash("Login successful", 'success')
                return redirect(url_for('view_customers'))
            elif user[0]['email'] == customer[0]['email'] and customer[0]['isActive'] == 1:
                session['name'] = user[0]['id'] 
                flash("Login successful", 'success')
                return redirect(url_for('home'))
            else:
                flash("Invalid User")
                return redirect(url_for("login"))
        else:
            flash("Invalid User")
            return redirect(url_for("login"))

    return render_template("login.html", title="login", email=email, password=password)

@app.route("/adminhome")
def admin_dashboard():
    # Add logic to display admin-related information
    return render_template("adminhome.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']

        if not full_name or not email or not address:
            flash('Please fill in all fields', 'error')
        else:
            # Use the addrecord function to insert data into the 'customers' table
            addrecord('customers', name=full_name, email=email, address=address)

            # Use the addrecord function to insert data into the 'users' table
            addrecord('users', email=email, password=password, isAdmin=False)

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/change_password', methods=['POST'])
def change_password_route():
    if request.method == 'POST':
        change_password(session.get("name"), request.form.get('new_password'))
        user_id = session.get("name")
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password == confirm_password:
            result = change_password(user_id, new_password)
            print(result)  # Print the result of change_password
            if result:
                return redirect(url_for('login'))
            else:
                print("Password change failed.")
        else:
            print("Passwords do not match.")

    return render_template('home.html')

@app.route("/customers", methods=['GET', 'POST'])
def view_customers():
    customer = get_active_customers()
    return render_template("admincustomer.html", title="Active Customer List", customers=customer)


# Route to add a new customer
@app.route("/customers/add", methods=['POST'])
def add_customer_route():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']

        if name and email and address:
            if addrecord('customers', name=name, email=email, address=address, isActive=True):
                flash('Customer added successfully!', 'success')
            else:
                flash('Failed to add customer.', 'error')
        else:
            flash('Invalid input. Please fill in all fields.', 'error')

    return redirect(url_for('view_customers'))

@app.route("/customers/get/<int:customer_id>")
def get_customer_details(customer_id):
    try:
        customer_list = getrecord('customers', id=customer_id)
        if customer_list:
            customer = customer_list[0]  # Assuming the first element of the list
            return jsonify({
                'id': customer['id'],
                'name': customer['name'],
                'email': customer['email'],
                'address': customer['address']
            })
    except Exception as e:
        print(f"Error in get_customer_details: {e}")
        return jsonify({'error': f'Internal server error: {e}'}), 500
    else:
        return jsonify({'error': 'Customer not found'}), 404

# Route to update customer details
@app.route("/customers/update/<int:customer_id>", methods=['POST'])
def update_customer_route(customer_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']

        if name and email and address:
            if updaterecord('customers', id=customer_id, name=name, email=email, address=address):
                flash('Customer updated successfully!', 'success')
            else:
                flash('Failed to update customer.', 'error')
        else:
            flash('Invalid input. Please fill in all fields.', 'error')

    return redirect(url_for('view_customers'))

@app.route("/customers/delete/<int:customer_id>")
def delete_customer_route(customer_id):
    if mark_customer_inactive(customer_id):
        flash('Customer marked as inactive successfully!', 'success')
    else:
        flash('Failed to mark customer as inactive.', 'error')

    return redirect(url_for('view_customers'))

@app.route('/searchcustomer', methods=['GET', 'POST'])
def searchcustomer():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        results = search_customers(search_query)
        return render_template('admincustomer.html', customers=results, search_query=search_query)
    return redirect(url_for('view_customers'))  # Redirect to the home page or the page where you display the items

@app.route("/items", methods=['GET'])
def view_items():
    items = getall('items')
    return render_template("adminitem.html", title="Active Item List", items=items)

# Route to add a new item
# Route to add a new item
@app.route("/items/add", methods=['POST'])
def add_item_route():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        item_type = request.form['type']
        price = request.form['price']
        qty = request.form['qty']

        # Check if the ISBN is available
        existing_item = getrecord('items', isbn=isbn)
        if existing_item:
            flash('ISBN is already taken. Please choose a different ISBN.', 'error')
        else:
            if isbn and title and author and genre and item_type and price and qty:
                if addrecord('items', isbn=isbn, title=title, author=author, genre=genre, type=item_type, price=price, qty=qty):
                    flash('Item added successfully!', 'success')
                else:
                    flash('Failed to add item.', 'error')
            else:
                flash('Invalid input. Please fill in all fields.', 'error')

    return redirect(url_for('view_items'))
# Route to update item details
@app.route("/items/update/<int:item_id>", methods=['POST'])
def update_item_route(item_id):
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        item_type = request.form['type']
        price = request.form['price']
        qty = request.form['qty']

        if isbn and title and author and genre and item_type and price and qty:
            if updaterecord('items', id=item_id, isbn=isbn, title=title, author=author, genre=genre, type=item_type, price=price, qty=qty):
                flash('Item updated successfully!', 'success')
            else:
                flash('Failed to update item.', 'error')
        else:
            flash('Invalid input. Please fill in all fields.', 'error')

    return redirect(url_for('view_items'))

@app.route("/items/get/<int:item_id>")
def get_item_details(item_id):
    try:
        item_list = getrecord('items', id=item_id)
        if item_list:
            item = item_list[0]  # Assuming the first element of the list
            return jsonify({
                'id': item['id'],
                'isbn': item['isbn'],
                'title': item['title'],
                'author': item['author'],
                'genre': item['genre'],
                'type': item['type'],
                'price': item['price'],
                'qty': item['qty']
            })
    except Exception as e:
        print(f"Error in get_item_details: {e}")
        return jsonify({'error': f'Internal server error: {e}'}), 500
    else:
        return jsonify({'error': 'Item not found'}), 404


@app.route("/items/delete/<int:item_id>")
def delete_item_route(item_id):
    orders = getall('order_items')

    for order in orders:
        if item_id == order['item_id']:
            flash('Failed to delete item. Item is being ordered in process', 'error')
            return jsonify(success=False, error='Item is being ordered in process')

    if deleterecord('items', id=item_id):
        flash('Item deleted successfully!', 'success')
        return jsonify(success=True)

    return jsonify(success=False, error='Failed to delete item')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        results = search_items(search_query)
        return render_template('adminitem.html', items=results, search_query=search_query)
    return redirect(url_for('view_items'))  # Redirect to the home page or the page where you display the items


@app.route("/logout")
def logout():
    if "name" in session:
        session.pop("name", None)  
        flash("Logged Out")
        return render_template("login.html")

@app.route("/home")
def home()->None:
    # Assuming you have a function to get the highest-selling books ISBNs
    highest_selling_isbns = [1, 2, 3, 4, 5]

    # Get the highest-selling books
    highest_selling_books = get_highest_selling_books(highest_selling_isbns)
    print(highest_selling_books)
    return render_template("home.html", highest_selling_books=highest_selling_books)

@app.route("/cart")
def get_cart():
 
    if "name" not in session:
        flash("User not logged in.", "error")
        return redirect(url_for("home"))

  
    user_id = session['name']
    cart_items = get_user_cart_items(user_id)


    total_items = sum(item['quantity'] for item in cart_items)
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

   
 
    return render_template("cart.html", cart_items=cart_items, total_items=total_items, total_price=total_price)

def add_to_cart(user_id: int, item_id: int, quantity: int) -> bool:
    try:
        # Check if the item quantity is greater than 0
        item = getrecord("items", id=item_id)
        itemqty = int(item[0]['qty']) if item and item[0]['qty'] else 0

        if itemqty <= 0:
            return False

        existing_cart_user = getuser("cart", cust_id=user_id, item_id=item_id)

        # If the item is already in the cart, check if adding the specified quantity exceeds the available quantity
        if existing_cart_user:
            current_quantity_in_cart = int(existing_cart_user[0]['quantity'])
            available_quantity = int(itemqty)

            if int(current_quantity_in_cart) + int(quantity) > available_quantity:
                return False

            new_quantity = int(current_quantity_in_cart) + int(quantity)
            return updaterecord("cart", id=existing_cart_user[0]['id'], quantity=new_quantity)
        else:
            # If the item is not in the cart, check if adding the specified quantity exceeds the available quantity
            available_quantity = int(itemqty)

            if int(quantity) > available_quantity:
                return False

            return addrecord("cart", cust_id=user_id, item_id=item_id, quantity=int(quantity))
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        return False

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart_route():
    if request.method == "POST":
        if "name" not in session:
            flash("User not logged in.", "error")
            return redirect(url_for("home"))

        user_id = session['name']
        item_id = request.form.get("item_id")
        quantity = request.form.get("quantity", 1)

        # Get the item details to check the available quantity
        item = getrecord("items", id=item_id)
        if not item:
            flash("Item not found.", "error")
            return redirect(url_for("get_cart"))

        available_quantity = int(item[0]['qty']) if item[0]['qty'] else 0

        # Check if the requested quantity exceeds the available quantity
        if int(quantity) > available_quantity:
            flash("Failed to add item to the cart. Insufficient quantity available.", "error")
            return redirect(url_for("get_cart"))

        # Proceed to add the item to the cart
        if add_to_cart(user_id, item_id, quantity):
            return redirect(url_for("get_cart"))
        else:
            flash("Failed to add item to the cart.", "error")

    return redirect(url_for("get_cart"))
@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart_route():
    if "name" not in session:
        flash("User not logged in.", "error")
        return redirect(url_for("home"))

    user_id = session['name']
    item_id = request.form.get("item_id")
      
    if deleterecord("cart", item_id=item_id):
        flash("Item removed from the cart.", "success")
        return redirect(url_for("get_cart"))
    else:
        flash("Failed to remove item from the cart.", "error")
        return redirect(url_for("get_cart"))

    return redirect(url_for("get_cart"))

def update_cart_item_quantity(item_id: int, new_quantity: int) -> bool:
    return updaterecord("cart", item_id=item_id, quantity=new_quantity)

@app.route("/update_quantity", methods=["POST"])
def update_quantity_route():
    if request.method == "POST":
      
        item_id = int(request.form.get("item_id"))
        new_quantity = int(request.form.get("new_quantity"))

        # Call the function to update the quantity in the cart
        if update_cart_item_quantity(item_id, new_quantity):
            return "Quantity updated successfully!"
        else:
            return "Failed to update quantity."
            
def calculate_total_items(cart_items: list) -> int:

    total_items = sum(item['quantity'] for item in cart_items)
    return total_items

def calculate_total_price(cart_items: list) -> float:
  
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return total_price

def process_checkout(user_id):
    cart_items = get_user_cart_items(user_id)

    if not cart_items:
        return False, "Your cart is empty."

    for item in cart_items:
        # Check if the item quantity is still sufficient
        if item["quantity"] > item["qty"]:
            return False, f"Insufficient quantity for item: {item['title']}"

    customer_details = get_customer_details(user_id)
    customer_name = customer_details.get("name", "Customer")
    total_items = calculate_total_items(cart_items)
    total_price = calculate_total_price(cart_items)
    order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order_id = addrecord("orders", cust_id=user_id, order_time=order_time, total_items=total_items, total_price=total_price)

    if order_id:
        for item in cart_items:
            addrecord("order_items", order_id=order_id, item_id=item["id"], quantity=item["quantity"], subtotal=item["price"] * item["quantity"])
            new_quantity = item["qty"] - item["quantity"]
            updaterecord("items", id=item["id"], qty=new_quantity)
        
        # Clear the user's cart after a successful checkout
        deleterecord("cart", cust_id=user_id)
        return True, "Checkout successful."

    return False, "Failed to process checkout."

@app.route("/checkout", methods=["GET"])
def checkout():
    if request.method == "GET":
        user_id = session.get('name')  # Assuming 'name' contains user_id
        customer_email = get_customer(user_id)

        if customer_email:
            cart_items = get_user_cart_items(user_id)

            for item in cart_items:
                # Check if the item quantity is still sufficient
                if item["quantity"] > item["qty"]:
                    flash(f"Insufficient quantity for item: {item['title']}", "error")
                    return redirect(url_for("get_cart"))

            total_items = calculate_total_items(cart_items)
            total_price = calculate_total_price(cart_items)

            return render_template("order.html", customer_details=customer_email, cart_items=cart_items, total_items=total_items, total_price=total_price)
        else:
            flash("Error retrieving customer details.", "error")
            return redirect(url_for("home"))

    return redirect(url_for("home"))

@app.route("/order", methods=["POST"])
def checkoutOrder():
    if request.method == "POST":
        user_id = session.get('name')
        ship = request.form.get('ship') 
            
        cart_items = get_user_cart_items(user_id)

        if not cart_items:
            return render_template("home.html", message="Your cart is empty.")

        total_items = calculate_total_items(cart_items)
        total_price = calculate_total_price(cart_items)
        order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

     
        order = addrecord("orders", customer_id=user_id, shipping_address=ship, total_price=total_price, created_at=order_time)

        if order:
            for item in cart_items:
                orders = getall('orders')
                order_id = orders[-1]['id']
                addrecord("order_items", order_id=order_id, item_id=item["id"], quantity=item["quantity"], subtotal=item["price"] * item["quantity"])

                new_quantity = item["qty"] - item["quantity"]
                updaterecord("items", id=item["id"], qty=new_quantity)
                deleterecord("cart", cust_id=user_id)

            return redirect(url_for("order_history"))
        else:
            return render_template("cart.html", message="Error creating order. Please try again.")

@app.route('/order_history', methods=["GET"])
def order_history():
    try:
        user_id = session.get('name')
        order_history = get_order_history(user_id)

        return render_template('orderhistory.html', orders=order_history)

    except Exception as e:
        print(e)
        return render_template("orderhistory.html", message="Error retrieving order history. Please try again.")


@app.route('/books', methods=['GET'])
def all_books():
    books = getall('items')
    return render_template('book.html', books=books)

@app.route('/searchbook', methods=['GET', 'POST'])
def searchbook():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        results = search_items(search_query)
        books = getall('items')
        return render_template('book.html', items=results, search_query=search_query, books=books)
    return redirect(url_for('all_books')) 

@app.route('/book/<int:book_id>', methods=['GET'])
def book_details(book_id):
    books = getall('items')
    book_details = getrecord('items', id = book_id)
    if book_details:
        return render_template('bookpage.html', book=book_details)
    else:
        return render_template('book.html', message='Book not found.')



@app.route("/")
def main()->None:
	return render_template("login.html")
	
if __name__=="__main__":
	app.run(host="0.0.0.0",debug=True)
	