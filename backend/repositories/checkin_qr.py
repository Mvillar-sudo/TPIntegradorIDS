from mysql.connector import Error as MySQLError

try:
    from db import get_db_connection
except ImportError:
    from backend.db import get_db_connection


def _obtener_conexion():
    conn = get_db_connection()
    if conn is None:
        raise MySQLError("No se pudo establecer conexión con la base de datos")
    return conn


"""
Pre: 'token_qr' es un string no vacío.
Post: Devuelve un diccionario con los datos del turno y del paciente si existe. Si no existe devuelve None.
"""
def buscar_turno_por_qr(token_qr):
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                t.id_turno,
                t.id_medico,
                t.id_paciente,
                t.id_consultorio,
                t.fecha_hora,
                t.estado,
                t.token_qr,
                t.fecha_hora_checkin,
                u.nombre_usuario AS paciente_nombre,
                u.apellido_usuario AS paciente_apellido
            FROM turnos t
            INNER JOIN usuarios u ON t.id_paciente = u.id_usuario
            WHERE t.token_qr = %s
        """
        cursor.execute(query, (token_qr,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


"""
Pre: 'id_turno' es un entero positivo y 'fecha_hora_checkin' es un objeto datetime válido.
Post: Actualiza el estado del turno a 'confirmado' y registra la fecha y hora de check-in. 
Devuelve True si se actualizó al menos una fila. En caso contrario devuelve False.
"""
def confirmar_checkin_turno(id_turno, fecha_hora_checkin):
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE turnos
            SET estado = 'confirmado',
                fecha_hora_checkin = %s
            WHERE id_turno = %s AND estado = 'reservado'
        """
        cursor.execute(query, (fecha_hora_checkin, id_turno))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        if conn is not None and conn.is_connected():
            conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


"""
Pre: 'id_turno' es un entero positivo.
Post: Actualiza el estado del turno a 'ausente' y devuelve True si se actualizó al menos una fila. En caso contrario devuelve False.
"""
def actualizar_turno_a_ausente(id_turno):
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE turnos
            SET estado = 'ausente'
            WHERE id_turno = %s AND estado = 'reservado'
        """
        cursor.execute(query, (id_turno,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        if conn is not None and conn.is_connected():
            conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
