from db import get_connection
from repositories.consultas_repositories import ejecutar_consulta


def obtener_turnos_disponibles(medico_id=None, fecha=None, especialidad_id=None):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT
                t.id_turno,
                t.id_medico,
                u.nombre_usuario AS nombre_medico,
                u.apellido_usuario AS apellido_medico,
                e.id_especialidad,
                e.nombre_especialidad,
                t.id_consultorio,
                c.numero_consultorio,
                c.piso,
                t.fecha_hora,
                t.estado
            FROM turnos t
            INNER JOIN medicos m
                ON t.id_medico = m.id_medico
            INNER JOIN usuarios u
                ON m.id_usuario = u.id_usuario
            INNER JOIN especialidades e
                ON m.id_especialidad = e.id_especialidad
            INNER JOIN consultorios c
                ON t.id_consultorio = c.id_consultorio
            WHERE t.estado = 'disponible'
        """

        parametros = []

        if medico_id is not None:
            query += " AND t.id_medico = %s"
            parametros.append(medico_id)

        if especialidad_id is not None:
            query += " AND e.id_especialidad = %s"
            parametros.append(especialidad_id)

        if fecha is not None:
            query += " AND DATE(t.fecha_hora) = %s"
            parametros.append(fecha)

        query += " ORDER BY t.fecha_hora ASC;"

        cursor.execute(query, tuple(parametros))
        resultados = cursor.fetchall()

        return resultados

    except Exception as e:
        print(f"Error al obtener turnos disponibles: {e}")
        return None

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()


def reservar_turno(id_turno, id_paciente, codigo_qr_hash):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        # 1. Consultar el turno.
        query_select = """
            SELECT id_turno, id_medico, fecha_hora, estado
            FROM turnos
            WHERE id_turno = %s;
        """

        cursor.execute(query_select, (id_turno,))
        turno = cursor.fetchone()

        if turno is None:
            return {"estado": "no_encontrado"}

        if turno["estado"] != "disponible":
            return {"estado": "no_disponible"}

        # 2. Reservar el turno.
        query_update = """
            UPDATE turnos
            SET id_paciente = %s,
                estado = 'reservado',
                token_qr = %s
            WHERE id_turno = %s
              AND estado = 'disponible';
        """

        cursor.execute(
            query_update,
            (id_paciente, codigo_qr_hash, id_turno)
        )

        # Comprobar que se haya actualizado una fila.
        if cursor.rowcount != 1:
            conexion.rollback()
            return {"estado": "no_disponible"}

        conexion.commit()

        return {
            "estado": "reservado",
            "turno": turno
        }

    except Exception as e:
        if conexion is not None:
            conexion.rollback()

        print(f"Error al reservar turno: {e}")
        return {"estado": "error"}

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()


def registrar_cancelacion_turno(id_turno, fecha_hora_cancelacion):
    """
    Pre: 'id_turno' es un entero positivo y 'fecha_hora_cancelacion' es un datetime.
    Post: Si el turno está reservado, lo marca como cancelado con la fecha y hora de cancelación y
          crea un turno nuevo y disponible en la misma franja (mismo médico, consultorio y horario),
          para que otro paciente pueda reservarla. Las dos cosas se hacen juntas: o se hacen
          las dos o no se hace ninguna. Devuelve True si canceló el turno y False si ya no
          estaba reservado.
    """
    conexion = get_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE turnos
            SET estado = 'cancelado',
                fecha_hora_cancelacion = %s
            WHERE id_turno = %s AND estado = 'reservado'
        """, (fecha_hora_cancelacion, id_turno))

        if cursor.rowcount != 1:
            conexion.rollback()
            return False

        cursor.execute("""
            INSERT INTO turnos (id_medico, id_consultorio, fecha_hora, estado)
            SELECT id_medico, id_consultorio, fecha_hora, 'disponible'
            FROM turnos
            WHERE id_turno = %s
        """, (id_turno,))

        conexion.commit()
        return True

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def obtener_turnos_de_paciente(id_paciente):
    """
    Pre: 'id_paciente' es el id_usuario de un paciente (entero positivo).
    Post: Devuelve la lista de turnos del paciente (de más nuevo a más viejo) con los datos del
          médico, la especialidad y el consultorio. Si no tiene turnos devuelve una lista vacía.
    """
    return ejecutar_consulta(
        """
        SELECT t.id_turno, t.fecha_hora, t.estado, t.token_qr,
               um.nombre_usuario AS medico_nombre,
               um.apellido_usuario AS medico_apellido,
               e.nombre_especialidad AS especialidad,
               c.numero_consultorio, c.piso
        FROM turnos AS t
        JOIN medicos AS m ON m.id_medico = t.id_medico
        JOIN usuarios AS um ON um.id_usuario = m.id_usuario
        JOIN especialidades AS e ON e.id_especialidad = m.id_especialidad
        JOIN consultorios AS c ON c.id_consultorio = t.id_consultorio
        WHERE t.id_paciente = %s
        ORDER BY t.fecha_hora DESC
        """,
        (id_paciente,),
    )
