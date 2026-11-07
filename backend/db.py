import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Devuelve una conexión activa a MySQL leyendo directamente las variables de entorno.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "centro_medico"),
    )


def get_db_connection():
    """
    Alias de compatibilidad: devuelve la conexión o None si falla.
    """
    try:
        return get_connection()
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def execute_query(query, params=None, fetch_all=True):
    """
    Función utilitaria auxiliar de compatibilidad.
    """
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
