import mysql.connector
from mysql.connector import Error

try:
    from config import DB_CONFIG
except ImportError:
    from backend.config import DB_CONFIG


"""
Pre: -
Post: Devuelve una conexión activa a MySQL o None en caso de error.
"""
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

"""
Pre: 'query' es una sentencia SQL válida, 'params' es una tupla o lista opcional de parámetros.
Post: Ejecuta la consulta SQL y devuelve los resultados para SELECT o lastrowid para INSERT/UPDATE.
"""
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
