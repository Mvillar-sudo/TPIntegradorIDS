from mysql.connector import Error as MySQLError

from db import get_connection
from repositories.consultas_repositories import ejecutar_consulta
from constants import MEDICOS_BASE_SELECT


def listar_medicos(especialidad_id=None):
    query = MEDICOS_BASE_SELECT
    params = ()
    if especialidad_id is not None:
        query += ' WHERE m.id_especialidad = %s'
        params = (especialidad_id,)
    query += ' ORDER BY m.apellido_medico, m.nombre_medico, m.id_medico'
    return ejecutar_consulta(query, params)


def obtener_medico(medico_id):
    rows = ejecutar_consulta(MEDICOS_BASE_SELECT + ' WHERE m.id_medico = %s', (medico_id,))
    return rows[0] if rows else None


def especialidad_existe(specialty_id):
    rows = ejecutar_consulta(
        'SELECT id_especialidad FROM especialidades WHERE id_especialidad = %s',
        (specialty_id,),
    )
    return bool(rows)


def matricula_existe(matricula, excluding=None):
    query = 'SELECT id_medico FROM medicos WHERE matricula = %s'
    params = [matricula]
    if excluding is not None:
        query += ' AND id_medico <> %s'
        params.append(excluding)
    return bool(ejecutar_consulta(query, tuple(params)))


def crear_medico(values):
    return ejecutar_consulta(
        'INSERT INTO medicos '
        '(id_especialidad, nombre_medico, apellido_medico, matricula) '
        'VALUES (%s, %s, %s, %s)',
        (
            values['id_especialidad'], values['nombre_medico'],
            values['apellido_medico'], values['matricula'],
        ),
    )


def actualizar_medico(medico_id, values):
    assignments = ', '.join(f'{column} = %s' for column in values)
    ejecutar_consulta(
        f'UPDATE medicos SET {assignments} WHERE id_medico = %s',
        (*values.values(), medico_id),
    )


def tiene_dependencias(medico_id):
    rows = ejecutar_consulta(
        "SELECT 1 FROM agendas WHERE id_medico = %s UNION ALL "
        'SELECT 1 FROM turnos WHERE id_medico = %s LIMIT 1',
        (medico_id, medico_id),
    )
    return bool(rows)


def eliminar_medico(medico_id):
    ejecutar_consulta('DELETE FROM medicos WHERE id_medico = %s', (medico_id,))


eliminar = eliminar_medico


def obtener_medico_por_usuario_id(id_usuario):
    rows = ejecutar_consulta("SELECT id_medico FROM medicos WHERE id_usuario = %s", (id_usuario,))
    return rows[0] if rows else None


def obtener_turnos_hoy_por_medico(id_medico):
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
    return ejecutar_consulta(query, (id_medico,))


def buscar_turno_por_id(id_turno):
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
    rows = ejecutar_consulta(query, (id_turno,))
    return rows[0] if rows else None


def actualizar_turno_a_atendido(id_turno, id_medico):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if conn is None:
            raise MySQLError("No se pudo establecer conexión con la base de datos")
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


def obtener_medicos_por_especialidad(especialidad_id=None):
    query = """
        SELECT
            m.id_medico,
            m.nombre_medico AS nombre,
            m.apellido_medico AS apellido,
            m.id_especialidad,
            e.nombre_especialidad AS especialidad
        FROM medicos m
        INNER JOIN especialidades e
            ON m.id_especialidad = e.id_especialidad
    """
    params = ()
    if especialidad_id is not None:
        query += " WHERE m.id_especialidad = %s"
        params = (especialidad_id,)

    query += " ORDER BY m.apellido_medico ASC, m.nombre_medico ASC;"
    return ejecutar_consulta(query, params)
