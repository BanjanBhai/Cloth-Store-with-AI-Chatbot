import google.generativeai as genai
from database import get_db_connection

# Configure Gemini
genai.configure(api_key="AIzaSyBlYqRYTbqEzCp_wd7eCtyNliSxw6VSVRI")
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

def ask_chatbot(user_message):
    context = get_store_context()
    # Combine context with the user message
    full_prompt = f"{context}\n\nCustomer: {user_message}\nAssistant: (Remember to use double newlines before and after any table)"
    
    response = model.generate_content(full_prompt)
    return response.text