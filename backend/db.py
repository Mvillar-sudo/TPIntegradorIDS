import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'salud_integral'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def execute_query(query, params=None, fetch_all=True):
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    result = None
    try:
        cursor.execute(query, params or ())
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall() if fetch_all else cursor.fetchone()
        else:
            connection.commit()
            result = cursor.lastrowid
    except Error as e:
        print(f"Error ejecutando SQL: {e}")
    finally:
        cursor.close()
        connection.close()
        
    return result
