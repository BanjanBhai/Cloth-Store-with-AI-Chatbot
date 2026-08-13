from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from database import get_db_connection
from chatbot import ask_chatbot


app = Flask(__name__)
app.secret_key = "secret123" # Required for flashing messages

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")

    #pass user_id from session if logged in 
    user_id = session.get('user_id')

    bot_reply = ask_chatbot(user_message, user_id)
    return jsonify({reply: bot_reply})

@app.route('/api/admin/add', methods=['POST'])
def admin_add_product():
    data = request.json  # React sends data as JSON
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    stock = data.get('stock_quantity')
    description = data.get('description')

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO products (name, category, price, stock_quantity, description) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (name, category, price, stock, description))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Product added successfully!"}), 201

@app.route('/api/admin/delete/<int:product_id>', methods=['DELETE'])
def admin_delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Product deleted!"}), 200


# # --- CUSTOMER SIDE ---
# @app.route('/')
# def index():
#     search_query = request.args.get('search') # Get search text from URL
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
    
#     if search_query:
#         # Search for products matching the name
#         query = "SELECT * FROM products WHERE name LIKE %s"
#         cursor.execute(query, ('%' + search_query + '%',))
#     else:
#         cursor.execute("SELECT * FROM products")
        
#     products = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('index.html', products=products)

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password'] # In Day 3, we will learn to encrypt this!
        
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'customer')", (username, password))
#             conn.commit()
#             flash("Account created! Please login.")
#             return redirect(url_for('login'))
#         except:
#             flash("Username already exists.")
#         finally:
#             cursor.close()
#             conn.close()
#     return render_template('signup.html')

# @app.route('/buy/<int:product_id>')
# def buy_now(product_id):
#     if not session.get('user_id'):
#         flash("Please login to buy items!")
#         return redirect(url_for('login'))

#     user_id = session['user_id']
    
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     # 1. Get product price
#     cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
#     product = cursor.fetchone()
    
#     if product:
#         # 2. Create Order
#         cursor.execute("INSERT INTO orders (user_id, status) VALUES (%s, 'pending')", (user_id,))
#         order_id = cursor.lastrowid
        
#         # 3. Create Order Item
#         cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, 1, %s)", 
#                        (order_id, product_id, product['price']))
        
#         # 4. Create Payment (Simulation)
#         cursor.execute("INSERT INTO payments (order_id, amount, method) VALUES (%s, %s, 'COD')", (order_id, product['price']))
        
#         # 5. Create Shipment entry
#         cursor.execute("INSERT INTO shipments (order_id, status) VALUES (%s, 'pending')", (order_id,))
        
#         conn.commit()
#         flash("Order placed successfully! Track it in your profile.")
    
#     cursor.close()
#     conn.close()
#     return redirect(url_for('index'))

# @app.route('/product/<int:product_id>')
# def product_detail(product_id):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
    
#     # Fetch the specific product by ID
#     cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
#     product = cursor.fetchone()
    
#     cursor.close()
#     conn.close()
    
#     if product:
#         return render_template('product_detail.html', product=product)
#     else:
#         flash("Product not found!")
#         return redirect(url_for('index'))

# @app.route('/chat', methods=['POST'])
# def chat():
#     try:
#         user_data = request.json
#         user_message = user_data.get("message")
#         # Retrieve the user_id from the session (will be None if not logged in)
#         current_user_id = session.get('user_id')
#         if not user_message:
#             return jsonify({"reply": "I didn't hear anything!"})
            
#         bot_reply = ask_chatbot(user_message, current_user_id)

#         return jsonify({"reply": bot_reply})
    
#     except Exception as e:
#         print(f"Flask Route Error: {e}")
#         return jsonify({"reply": "Sorry, I am experiencing a server error."}), 500

# # --- ADMIN SIDE ---
# @app.route('/admin')
# def admin_dashboard():
#     if session.get('role') != 'admin':
#         flash("Unauthorized Access!")
#         return redirect(url_for('login'))
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM products")
#     products = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('admin.html', products=products)

# @app.route('/admin/add', methods=['POST'])
# def add_product():
#     name = request.form['name']
#     category = request.form['category']
#     price = request.form['price']
#     stock = request.form['stock']
#     description = request.form['description']

#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     sql = "INSERT INTO products (name, category, price, stock_quantity, description) VALUES (%s, %s, %s, %s, %s)"
#     values = (name, category, price, stock, description)
    
#     cursor.execute(sql, values)
#     conn.commit()
#     cursor.close()
#     conn.close()
    
#     flash("Product added successfully!")
#     return redirect(url_for('admin_dashboard'))

# @app.route('/admin/delete/<int:id>')
# def delete_product(id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM products WHERE id = %s", (id,))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return redirect(url_for('admin_dashboard'))

# # --- EDIT PRODUCT ROUTES ---

# @app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
# def edit_product(id):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     if request.method == 'POST':
#         name = request.form['name']
#         category = request.form['category']
#         price = request.form['price']
#         stock = request.form['stock']
#         description = request.form['description']

#         # Removed image_url from UPDATE statement
#         sql = """UPDATE products 
#                  SET name = %s, category = %s, price = %s, stock_quantity = %s, description = %s 
#                  WHERE id = %s"""
#         values = (name, category, price, stock, description, id)
#         cursor.execute(sql, values)
#         conn.commit()
        
#         cursor.close()
#         conn.close()
#         flash("Product updated successfully!")
#         return redirect(url_for('admin_dashboard'))

#     else:
#         cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
#         product = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         return render_template('edit_product.html', product=product)
    
# @app.route('/admin/orders')
# def manage_orders():
#     if session.get('role') != 'admin':
#         return redirect(url_for('login'))
    
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     query = """
#         SELECT o.id, u.username, o.order_date, s.status as ship_status, s.id as ship_id
#         FROM orders o
#         JOIN users u ON o.user_id = u.id
#         JOIN shipments s ON o.id = s.order_id
#         ORDER BY o.order_date DESC
#     """
#     cursor.execute(query)
#     orders = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('admin_orders.html', orders=orders)

# @app.route('/admin/update_shipment/<int:ship_id>/<string:new_status>')
# def update_shipment(ship_id, new_status):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("UPDATE shipments SET status = %s WHERE id = %s", (new_status, ship_id))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     flash(f"Shipment updated to {new_status}!")
#     return redirect(url_for('manage_orders'))
    
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
#         user = cursor.fetchone()
        
#         if user:
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             session['role'] = user['role']
#             flash("Login successful!")
#             if user['role'] == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             else:
#                 return redirect(url_for('index'))
            
#         else:
#             flash("Invalid credentials.")

        
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     #1 check login
#     if 'user_id' not in session:
#         return jsonify({"status": "unauthorized"}), 401
    
#     data = request.get_json()
#     product_id = str(data.get('product_id')) # session keys must be str

#     #2 initialize cart if not exist
#     if 'cart' not in session:
#         session['cart']={}

#     #3 update quantity. clicking multiple times increases count
#     cart = session['cart']
#     cart[product_id] = cart.get(product_id, 0) + 1

#     #4 reassign and mark as modified
#     session['cart'] = cart
#     session.modified = True

#     #5 calaculate total items for navbar badge
#     total_items = sum(cart.values()) 

#     return jsonify({"status": "success", "total_items": total_items, "message": "Item added to bag!"})

# @app.route('/cart')
# def view_cart():
#     if 'user_id' not in session: return redirect('/login')

#     cart = session.get('cart')
#     display_cart = []
#     grand_total = 0

#     if cart:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         #fetch only the proucts in session cart
#         placeholders = ', '.join(['%s'] * len(cart))
#         query = f"SELECT id, name, price FROM products WHERE id in({placeholders})"
#         cursor.execute(quesry, list(cart.keys()))
#         products = cursor.fetchall()

#         for p in products:
#             qty = cart[str(p['id'])]
#             subtotal=p['price']*qty
#             grand_total += subtotal
#             display_cart.append({
#                 'id':p['id'],
#                 'name':p['name'],
#                 'price':p['price'],
#                 'quantity': qty,
#                 'subtotal': subtotal
#             })

#         cursor.close()
#         conn.close()

#     return render_template('cart.html', cart=display_cart, grand_total=grand_total)

# @app.route('/checkout', methods=['POST'])
# def checkout():
#     user_id = session.get('user_id')
#     cart= session.get('cart')
#     payment_method = request.form.get('payment_method')

#     if not cart: return redirect('/')

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         #1 create one order record
#         cursor.execute("INSERT INTO orders (user_id, status) values (%s, 'paid')", (user_id,))
#         order_id=cursor.lastrowid

#         total_amount=0

#         #2 loop through session cart to create many order items
#         for p_id, qty in cart.items():
#             cursor.execute("SELECT price from products where id=%s", (p_id,))
#             price=cursor.fetchone()[0]

#             #insert into order_items
#             cursor.execute("""
#                 INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
#                 VALUES (%s, %s, %s, %s)
#                            """, (order_id, p_id, qty, price))
            
#             total_amount += (price*qty)

#         #3 create payment record
#         cursor.execute("""
#             INSERT INTO payments (order_id, amount, method) 
#             VALUES (%s, %s, %s) """, (order_id, total_amount, payment_method))
        
#         cursor.execute("INSERT INTO shipments (order_id, status) Values (%s, pending)", (order_id,))

#         #4 clear session after successful checkout
#         session.pop('cart', None)
#         conn.commit()

#         return render_template('checkout_success.html', order_id=order_id, total_amount=total_amount)
    
#     except Exception as e:
#         conn.rollback()
#         return f"Error: {str(e)}"
    
#     finally:
#         conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)