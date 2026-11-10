from mysql.connector import Error as MySQLError

from db import get_connection


"""
Pre: -
Post: Devuelve un objeto de conexión activo a la base de datos o lanza MySQLError si no se pudo conectar.
"""
def _obtener_conexion():
    conn = get_connection()
    if conn is None:
        raise MySQLError("No se pudo establecer conexión con la base de datos")
    return conn


"""
Pre: -
Post: Devuelve la lista de turnos confirmados y con check-in del día, ordenados de forma ascendente
      por horario de llegada (fecha_hora_checkin). Cada fila incluye datos del paciente, médico y consultorio.
"""
def obtener_turnos_sala_espera():
    conn = None
    cursor = None
    try:
        conn = _obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                t.id_turno,
                t.fecha_hora,
                t.fecha_hora_checkin,
                u.nombre_usuario AS paciente_nombre,
                u.apellido_usuario AS paciente_apellido,
                um.nombre_usuario AS medico_nombre,
                um.apellido_usuario AS medico_apellido,
                c.numero_consultorio,
                c.piso
            FROM turnos t
            INNER JOIN usuarios u ON t.id_paciente = u.id_usuario
            LEFT JOIN medicos m ON t.id_medico = m.id_medico
            LEFT JOIN usuarios um ON m.id_usuario = um.id_usuario
            LEFT JOIN consultorios c ON t.id_consultorio = c.id_consultorio
            WHERE t.estado = 'confirmado'
              AND t.fecha_hora_checkin IS NOT NULL
              AND (DATE(t.fecha_hora_checkin) = CURDATE() OR DATE(t.fecha_hora) = CURDATE())
            ORDER BY t.fecha_hora_checkin ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
