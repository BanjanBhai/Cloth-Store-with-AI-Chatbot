from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import get_db_connection

app = Flask(__name__)
app.secret_key = "secret123" # Required for flashing messages

# --- CUSTOMER SIDE ---
@app.route('/')
def index():
    search_query = request.args.get('search') # Get search text from URL
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if search_query:
        # Search for products matching the name
        query = "SELECT * FROM products WHERE name LIKE %s"
        cursor.execute(query, ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM products")
        
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # In Day 3, we will learn to encrypt this!
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'customer')", (username, password))
            conn.commit()
            flash("Account created! Please login.")
            return redirect(url_for('login'))
        except:
            flash("Username already exists.")
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

@app.route('/buy/<int:product_id>')
def buy_now(product_id):
    if not session.get('user_id'):
        flash("Please login to buy items!")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Get product price
    cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    
    if product:
        # 2. Create Order
        cursor.execute("INSERT INTO orders (user_id, status) VALUES (%s, 'pending')", (user_id,))
        order_id = cursor.lastrowid
        
        # 3. Create Order Item
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, 1, %s)", 
                       (order_id, product_id, product['price']))
        
        # 4. Create Payment (Simulation)
        cursor.execute("INSERT INTO payments (order_id, amount, method) VALUES (%s, %s, 'COD')", (order_id, product['price']))
        
        # 5. Create Shipment entry
        cursor.execute("INSERT INTO shipments (order_id, status) VALUES (%s, 'pending')", (order_id,))
        
        conn.commit()
        flash("Order placed successfully! Track it in your profile.")
    
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch the specific product by ID
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if product:
        return render_template('product_detail.html', product=product)
    else:
        flash("Product not found!")
        return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message').lower()
    user_id = session.get('user_id')
    
    # Default Reply
    reply = "I can help you with 'prices', 'products', or 'track my order'."

    if "track" in user_message or "status" in user_message:
        if not user_id:
            reply = "Please login first so I can find your orders!"
        else:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Find the latest shipment for this user
            query = """
                SELECT s.status, s.updated_at, p.name 
                FROM shipments s
                JOIN orders o ON s.order_id = o.id
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.user_id = %s
                ORDER BY s.updated_at DESC LIMIT 1
            """
            cursor.execute(query, (user_id,))
            order = cursor.fetchone()
            cursor.close()
            conn.close()

            if order:
                reply = f"Your latest order for '{order['name']}' is currently: **{order['status'].upper()}**. (Last update: {order['updated_at']})"
            else:
                reply = "You haven't placed any orders yet!"

    elif "price" in user_message:
        reply = "Our prices are very competitive! Most items are between $15 and $90."
    elif "hi" in user_message or "hello" in user_message:
        reply = "Hi there! Want to 'track an order' or 'browse products'?"

    return jsonify({"reply": reply})

# --- ADMIN SIDE ---
@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Unauthorized Access!")
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['POST'])
def add_product():
    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    stock = request.form['stock']
    description = request.form['description']

    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "INSERT INTO products (name, category, price, stock_quantity, description) VALUES (%s, %s, %s, %s, %s)"
    values = (name, category, price, stock, description)
    
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Product added successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# --- EDIT PRODUCT ROUTES ---

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        stock = request.form['stock']
        description = request.form['description']

        # Removed image_url from UPDATE statement
        sql = """UPDATE products 
                 SET name = %s, category = %s, price = %s, stock_quantity = %s, description = %s 
                 WHERE id = %s"""
        values = (name, category, price, stock, description, id)
        cursor.execute(sql, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        flash("Product updated successfully!")
        return redirect(url_for('admin_dashboard'))

    else:
        cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_product.html', product=product)
    
@app.route('/admin/orders')
def manage_orders():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT o.id, u.username, o.order_date, s.status as ship_status, s.id as ship_id
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN shipments s ON o.id = s.order_id
        ORDER BY o.order_date DESC
    """
    cursor.execute(query)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/update_shipment/<int:ship_id>/<string:new_status>')
def update_shipment(ship_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE shipments SET status = %s WHERE id = %s", (new_status, ship_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f"Shipment updated to {new_status}!")
    return redirect(url_for('manage_orders'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash("Login successful!")
            return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('index'))
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)