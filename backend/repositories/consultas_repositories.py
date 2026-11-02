from db import get_connection
from mysql.connector import Error


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

    except Error:
        connection.rollback()
        cursor.close()
        connection.close()
        raise

