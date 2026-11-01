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
Pre: 'id_usuario' es un entero positivo.
Post: Devuelve un diccionario con el id_medico si el usuario es médico. Si no es médico devuelve None.
"""
def obtener_medico_por_usuario_id(id_usuario):
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_medico FROM medicos WHERE id_usuario = %s", (id_usuario,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


"""
Pre: 'id_medico' es un entero positivo.
Post: Devuelve una lista de diccionarios con los turnos del día actual para el médico indicado, ordenados por hora de inicio.
Solo incluye turnos que tienen un paciente asignado.
"""
def obtener_turnos_hoy_por_medico(id_medico):
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                t.id_turno,
                t.fecha_hora,
                t.estado,
                t.token_qr,
                t.fecha_hora_checkin,
                u.nombre_usuario AS paciente_nombre,
                u.apellido_usuario AS paciente_apellido,
                u.dni_usuario AS paciente_dni
            FROM turnos t
            INNER JOIN usuarios u ON t.id_paciente = u.id_usuario
            WHERE t.id_medico = %s AND DATE(t.fecha_hora) = CURDATE()
            ORDER BY t.fecha_hora ASC
        """
        cursor.execute(query, (id_medico,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


"""
Pre: 'id_turno' es un entero positivo.
Post: Devuelve un diccionario con los datos del turno si existe.
"""
def buscar_turno_por_id(id_turno):
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                id_turno,
                id_medico,
                id_paciente,
                id_consultorio,
                fecha_hora,
                estado,
                token_qr,
                fecha_hora_checkin
            FROM turnos
            WHERE id_turno = %s
        """
        cursor.execute(query, (id_turno,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


"""
Pre: 'id_turno' es un entero positivo, 'id_medico' es un entero positivo.
Post: Actualiza el estado del turno a 'atendido' si pertenece al médico y está en estado 'confirmado'.
      Devuelve True si se actualizó al menos una fila. En caso contrario devuelve False.
"""
def actualizar_turno_a_atendido(id_turno, id_medico):
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE turnos
            SET estado = 'atendido'
            WHERE id_turno = %s AND id_medico = %s AND estado = 'confirmado'
        """
        cursor.execute(query, (id_turno, id_medico))
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
