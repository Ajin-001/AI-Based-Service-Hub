import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",  # Use 127.0.0.1 instead of "localhost" for XAMPP
            user="root",  # XAMPP default user is "root"
            password="",  # Default password is empty in XAMPP (change if needed)
            database="chatbot_project",  # Ensure this database exists in phpMyAdmin
            port=3306  # XAMPP MySQL default port
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None
