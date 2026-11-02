import mysql.connector
import os
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host = os.getenv("DB_HOST", "localhost"),
            port = int(os.getenv("DB_PORT", "3306")),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD")
    )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def ejecutar_consulta(query, params=None, fetch_all=True):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if cursor.description is not None:
            if fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
        else:
            connection.commit()
            result = cursor.lastrowid

        cursor.close()
        connection.close()

        return result

    except mysql.connector.Error:
        connection.rollback()
        cursor.close()
        connection.close()
        raise

