from database import get_db_connection
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini #
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_store_context():
    """Fetch all products from DB to give the AI 'knowledge' of our store."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, price, stock_quantity, description FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    context = """You are 'TrendAssistant', a high-end fashion concierge. 
    IMPORTANT FORMATTING RULES:
    1. If a user asks for prices, ALWAYS respond with a clean Markdown Table.
    2. Use bold text for product names.
    3. Use emojis sparingly to look modern.
    4. Keep paragraphs short and stylish.
    
    Current Inventory:
    """
    for p in products:
        context += f"- {p['name']}: ${p['price']} ({p['stock_quantity']} in stock). {p['description']}\n"
    
    context += "\nIf a customer asks for something we don't have, suggest the closest alternative. Be stylish and polite."
    return context

def get_order_context(user_id=1):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)


    #query to join orders and shipments to get recent order history with payment and shipping status
    sql= """
        Select o.id, o.order_date, o.status as order_status, s.tracking_number, s.carrier as shipping_status
        from orders o 
        left join shipments s on o.id = s.order_id
        where o.user_id = %s
        order by o.order_date desc
        limit 5    
    """
    cursor.execute(sql, (user_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()

    if not orders:
        return "There are no recent orders."
    
    context="\nUser's Recent Order History:\n"
    for o in orders:
        context+= f"- Order #{o['id']} (Date: {o['order_date']}): "
        context+= f"Payment Status: {o['order_status']}, "
        context+= f"Shipping Status: {o['shipping_status']} "
        context+= f"Tracking: {o['tracking_number'] if o['tracking_number'] else 'N/A'}\n"
    
    return context

def get_user_order_context(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        select o.id, o.status, o.order_date, MAX(s.tracking_number) as tracking_number, MAX(s.status) as ship_status,
               group_concat(concat(p.name, ' (qty: ', oi.quantity, ')') separator ', ') as items
        from orders o
        join order_items oi on o.id = oi.order_id
        join products p on oi.product_id = p.id
        left join shipments s on o.id = s.order_id
        where o.user_id = %s
        group by o.id, o.status, o.order_date
        order by o.order_date desc
    """

    cursor.execute(sql, (user_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()

    if not orders:
        return "You have no recent orders."
    
    context = "\n### Current User's Order History ###\n"

    for o in orders:
        context += f"- Order #{o['id']}: Status: {o['status']} | Items: {o['items']} | Tracking: {o['tracking_number']} ({o['ship_status']})\n"

    return context

def ask_chatbot(user_message, user_id=None):
    #get inventory context
    inventory = get_store_context()
    #get order list for user
    user_context = get_user_order_context(user_id)

    prompt = f"""You are 'TrendAssistant', a high-end fashion concierge.
    {inventory}
    {user_context}

    Instructions:
    1. If the user asks 'my order' or 'tracking' look at the order history provided above.
    2. If they aren't logged in (user_id is None), ask them to log in to see orders.
    3. NEVER show order IDs or info that isn't in the provided History.
    
    User says: {user_message}
    Assistant:
    """

    response = model.generate_content(prompt)
    return response.text