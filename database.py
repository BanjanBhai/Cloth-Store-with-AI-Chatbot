import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",         # Your MySQL username
        password="iphone6S369248!mysql", # Your MySQL password
        database="cloth_store" # Your MySQL database name
    )
    return connection 
