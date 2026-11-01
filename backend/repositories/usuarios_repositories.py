from db import get_connection

def obtener_usuario_por_email(email):
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT * FROM usuarios
            WHERE email_usuario = %s
            """, 
            (email,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conexion.close()

def crear_usuario(nombre, apellido, dni, email, password_hash, telefono=None, id_cobertura=None):
    conexion = get_connection()
    cursor = None

    try:
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios(rol_usuario, nombre_usuario, apellido_usuario, dni_usuario, email_usuario, password_hash, telefono_usuario, id_cobertura)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            ("paciente", nombre, apellido, dni, email, password_hash, telefono, id_cobertura)
        )

        conexion.commit()

        return cursor.lastrowid

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()