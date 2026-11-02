from db import get_connection


def obtener_especialidades():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT id_especialidad, nombre_especialidad
            FROM especialidades
            ORDER BY nombre_especialidad ASC;
        """

        cursor.execute(query)
        resultados = cursor.fetchall()

        return resultados

    except Exception as e:
        print(f"Error al obtener las especialidades: {e}")
        return None

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()